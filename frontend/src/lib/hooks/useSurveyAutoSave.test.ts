import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';

// --- Mocks -----------------------------------------------------------------

const saveOrUpdateResponse = vi.fn().mockResolvedValue('response-1');
const getResponseByBusinessAndStandard = vi.fn().mockResolvedValue(null);
const markResponseCompleted = vi.fn().mockResolvedValue(undefined);

vi.mock('@/lib/firebase/responses', () => ({
  saveOrUpdateResponse: (...a: unknown[]) => saveOrUpdateResponse(...a),
  getResponseByBusinessAndStandard: (...a: unknown[]) => getResponseByBusinessAndStandard(...a),
  markResponseCompleted: (...a: unknown[]) => markResponseCompleted(...a),
  calculateProgress: (all: string[], answered: string[]) => ({
    totalQuestions: all.length,
    answeredQuestions: answered.length,
    percentComplete: all.length ? Math.round((answered.length / all.length) * 100) : 0,
  }),
}));

vi.mock('@/lib/contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { uid: 'user-1' },
    activeBusiness: { rut: '11111111-1' },
  }),
}));

import { useSurveyAutoSave } from './useSurveyAutoSave';

const options = {
  standardId: 'std-1',
  standardActions: { q1: { action: 'q1', valid_answers: ['yes', 'no'] } },
  debounceMs: 2000,
  enableAutoSave: true,
};

describe('useSurveyAutoSave', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    saveOrUpdateResponse.mockClear();
    getResponseByBusinessAndStandard.mockClear();
  });

  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

  it('debounces the save: fires once after the debounce window elapses', async () => {
    const { result } = renderHook(() => useSurveyAutoSave(options));

    // Flush the initial 200ms load effect.
    await act(async () => {
      await vi.advanceTimersByTimeAsync(200);
    });

    act(() => {
      result.current.setSelectedAnswers({ q1: 'yes' });
    });

    // Not yet saved before the debounce window elapses.
    expect(saveOrUpdateResponse).not.toHaveBeenCalled();

    await act(async () => {
      await vi.advanceTimersByTimeAsync(2000);
    });

    expect(saveOrUpdateResponse).toHaveBeenCalledTimes(1);
    const saved = saveOrUpdateResponse.mock.calls[0][0];
    expect(saved.business_rut).toBe('11111111-1');
    expect(saved.standard_template).toBe('std-1');
    expect(saved.user_id).toBe('user-1');
    expect(saved.answers).toHaveLength(1);
    expect(saved.answers[0]).toMatchObject({ standard_code: 'q1', answer_value: 'yes' });
  });

  it('collapses rapid successive edits into a single save', async () => {
    const { result } = renderHook(() => useSurveyAutoSave(options));
    await act(async () => {
      await vi.advanceTimersByTimeAsync(200);
    });

    act(() => result.current.setSelectedAnswers({ q1: 'yes' }));
    await act(async () => {
      await vi.advanceTimersByTimeAsync(500);
    });
    act(() => result.current.setSelectedAnswers({ q1: 'no' }));

    await act(async () => {
      await vi.advanceTimersByTimeAsync(2000);
    });

    expect(saveOrUpdateResponse).toHaveBeenCalledTimes(1);
    expect(saveOrUpdateResponse.mock.calls[0][0].answers[0].answer_value).toBe('no');
  });

  it('cancels the pending save when the component unmounts', async () => {
    const { result, unmount } = renderHook(() => useSurveyAutoSave(options));
    await act(async () => {
      await vi.advanceTimersByTimeAsync(200);
    });

    act(() => {
      result.current.setSelectedAnswers({ q1: 'yes' });
    });

    unmount();

    await act(async () => {
      await vi.advanceTimersByTimeAsync(5000);
    });

    expect(saveOrUpdateResponse).not.toHaveBeenCalled();
  });
});
