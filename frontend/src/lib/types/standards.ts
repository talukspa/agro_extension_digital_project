// Canonical type for a survey response
export interface Response {
  business_rut: string;
  is_completed: boolean;
  date: string; // ISO date string
  answers: Answer[];
  auditor_id: string;
}

// Canonical type for an answer
export interface Answer {
  action: Action; // See below
  answer_value: string | number | boolean | any[] | Record<string, any>;
  // Optionally, if action.verification_type === 'image', may include:
  register?: {
    image_url: string;
    [key: string]: any;
  };
}

// Minimal Action type (expand as needed from standard.json)
export interface Action {
  id: string;
  description: string;
  verification_type: string;
  theme?: string;
  points?: number;
  [key: string]: any;
}
