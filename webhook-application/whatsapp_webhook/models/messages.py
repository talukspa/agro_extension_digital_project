"""
Pydantic v2 models for WhatsApp webhook message processing.

These domain models provide type safety, validation, and clear structure
for handling WhatsApp webhook payloads, agent communications, and outgoing messages.
Supports all WhatsApp message types: text, image, audio, video, document, location, contacts, etc.
"""

from typing import List, Optional, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re


# Base classes for different message content types

class WhatsAppTextContent(BaseModel):
    """Text content of a WhatsApp message."""
    
    model_config = ConfigDict(extra="allow")
    
    body: str = Field(..., min_length=1, max_length=4096, description="Message text content")


class WhatsAppMediaContent(BaseModel):
    """Base class for media content (image, audio, video, document)."""
    
    model_config = ConfigDict(extra="allow")
    
    id: Optional[str] = Field(None, description="Media ID")
    mime_type: Optional[str] = Field(None, description="MIME type of the media")
    sha256: Optional[str] = Field(None, description="SHA256 hash of the media")
    caption: Optional[str] = Field(None, description="Media caption")


class WhatsAppImageContent(WhatsAppMediaContent):
    """Image content specific fields."""
    pass


class WhatsAppAudioContent(WhatsAppMediaContent):
    """Audio content specific fields."""
    voice: Optional[bool] = Field(None, description="Whether it's a voice message")


class WhatsAppVideoContent(WhatsAppMediaContent):
    """Video content specific fields."""
    pass


class WhatsAppDocumentContent(WhatsAppMediaContent):
    """Document content specific fields."""
    filename: Optional[str] = Field(None, description="Document filename")


class WhatsAppStickerContent(WhatsAppMediaContent):
    """Sticker content specific fields."""
    animated: Optional[bool] = Field(None, description="Whether the sticker is animated")


class WhatsAppLocationContent(BaseModel):
    """Location content of a WhatsApp message."""
    
    model_config = ConfigDict(extra="allow")
    
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    name: Optional[str] = Field(None, description="Location name")
    address: Optional[str] = Field(None, description="Location address")
    url: Optional[str] = Field(None, description="Location URL")


class WhatsAppContactsContent(BaseModel):
    """Contacts content of a WhatsApp message."""
    
    model_config = ConfigDict(extra="allow")
    
    # Contacts are typically an array, but structure can vary
    # Using flexible Dict to accommodate different contact formats


class WhatsAppInteractiveReply(BaseModel):
    """El botón o la fila que tocó el usuario."""

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = Field(None, description="Id del botón o fila (opt_N)")
    title: Optional[str] = Field(None, description="Título tocado")
    description: Optional[str] = Field(None, description="Descripción de la fila, si tenía")


class WhatsAppInteractiveContent(BaseModel):
    """Interactive content (buttons, lists, etc.)."""

    model_config = ConfigDict(extra="allow")

    type: Optional[str] = Field(None, description="Interactive type")
    button_reply: Optional[WhatsAppInteractiveReply] = Field(None, description="Botón tocado")
    list_reply: Optional[WhatsAppInteractiveReply] = Field(None, description="Fila tocada")


class WhatsAppReactionContent(BaseModel):
    """Reaction content of a WhatsApp message."""
    
    model_config = ConfigDict(extra="allow")
    
    message_id: str = Field(..., description="ID of the message being reacted to")
    emoji: Optional[str] = Field(None, description="Reaction emoji")


class WhatsAppSystemContent(BaseModel):
    """System message content."""
    
    model_config = ConfigDict(extra="allow")
    
    body: Optional[str] = Field(None, description="System message body")
    type: Optional[str] = Field(None, description="System message type")


# Main message model that can handle all types
class WhatsAppMessage(BaseModel):
    """Universal WhatsApp message that can handle all message types."""
    
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(..., min_length=1, description="Unique message ID")
    type: str = Field(..., description="Message type")
    timestamp: str = Field(..., description="Message timestamp")
    from_: str = Field(..., alias="from", description="Sender phone number")
    
    # Content fields for different message types (all optional)
    text: Optional[WhatsAppTextContent] = Field(None, description="Text content")
    image: Optional[WhatsAppImageContent] = Field(None, description="Image content")
    audio: Optional[WhatsAppAudioContent] = Field(None, description="Audio content")
    video: Optional[WhatsAppVideoContent] = Field(None, description="Video content")
    document: Optional[WhatsAppDocumentContent] = Field(None, description="Document content")
    sticker: Optional[WhatsAppStickerContent] = Field(None, description="Sticker content")
    location: Optional[WhatsAppLocationContent] = Field(None, description="Location content")
    contacts: Optional[List[Dict[str, Any]]] = Field(None, description="Contacts content")
    interactive: Optional[WhatsAppInteractiveContent] = Field(None, description="Interactive content")
    reaction: Optional[WhatsAppReactionContent] = Field(None, description="Reaction content")
    system: Optional[WhatsAppSystemContent] = Field(None, description="System message content")
    
    @field_validator('from_')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """Validate phone number format."""
        # Remove any whitespace and ensure it's a valid format
        phone = re.sub(r'\s+', '', v)
        if not re.match(r'^\+?[1-9]\d{1,14}$', phone):
            raise ValueError('Invalid phone number format')
        return phone
    
    def interactive_reply_text(self) -> Optional[str]:
        """El toque de un botón o fila como texto: "título — descripción".

        La descripción va porque el título solo ("Qué me falta") pierde el
        contexto del menú. None si no es un toque reconocible (p. ej. un Flow).
        """
        if self.type != "interactive" or not self.interactive:
            return None
        reply = self.interactive.button_reply or self.interactive.list_reply
        title = (reply.title or "").strip() if reply else ""
        if not title:
            return None
        description = (reply.description or "").strip()
        return f"{title} — {description}" if description else title

    def get_message_content(self) -> Optional[str]:
        """Extract readable content from any message type."""
        if self.type == "text" and self.text:
            return self.text.body
        elif self.type == "image" and self.image and self.image.caption:
            return f"[Image: {self.image.caption}]"
        elif self.type == "audio" and self.audio:
            voice_type = "Voice message" if self.audio.voice else "Audio"
            caption = f": {self.audio.caption}" if self.audio.caption else ""
            return f"[{voice_type}{caption}]"
        elif self.type == "video" and self.video:
            caption = f": {self.video.caption}" if self.video.caption else ""
            return f"[Video{caption}]"
        elif self.type == "document" and self.document:
            filename = self.document.filename or "Document"
            caption = f": {self.document.caption}" if self.document.caption else ""
            return f"[{filename}{caption}]"
        elif self.type == "location" and self.location:
            name = self.location.name or "Location"
            return f"[{name}: {self.location.latitude}, {self.location.longitude}]"
        elif self.type == "sticker":
            return "[Sticker]"
        elif self.type == "contacts":
            return "[Contact shared]"
        elif self.type == "interactive":
            return self.interactive_reply_text() or "[Interactive message]"
        elif self.type == "reaction" and self.reaction:
            emoji = self.reaction.emoji or "👍"
            return f"[Reaction: {emoji}]"
        elif self.type == "system" and self.system and self.system.body:
            return f"[System: {self.system.body}]"
        else:
            return f"[{self.type.title()} message]"
    
    def is_text_message(self) -> bool:
        """Check if this is a text message."""
        return self.type == "text" and self.text is not None


class WhatsAppContact(BaseModel):
    """Contact information from WhatsApp webhook."""
    
    model_config = ConfigDict(extra="allow")
    
    wa_id: str = Field(..., min_length=1, description="WhatsApp ID")
    profile: Optional[Dict[str, Any]] = Field(default=None, description="Profile information")


class WhatsAppMessageValue(BaseModel):
    """Value object containing messages and contacts from webhook."""
    
    model_config = ConfigDict(extra="allow")
    
    messaging_product: Optional[str] = Field(default="whatsapp", description="Messaging product")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata information")
    contacts: List[WhatsAppContact] = Field(default_factory=list, description="Contact information")
    messages: List[WhatsAppMessage] = Field(default_factory=list, description="List of messages")
    
    def get_sender_wa_id(self) -> Optional[str]:
        """Get the sender's WhatsApp ID from contacts."""
        if self.contacts:
            return self.contacts[0].wa_id
        return None


class WhatsAppChange(BaseModel):
    """Change object from WhatsApp webhook."""
    
    model_config = ConfigDict(extra="allow")
    
    field: str = Field(..., description="Change field type")
    value: WhatsAppMessageValue = Field(..., description="Change value containing messages")


class WhatsAppEntry(BaseModel):
    """Entry object from WhatsApp webhook."""
    
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(..., min_length=1, description="Entry ID")
    changes: List[WhatsAppChange] = Field(default_factory=list, description="List of changes")


class WhatsAppWebhookPayload(BaseModel):
    """Complete WhatsApp webhook payload."""
    
    model_config = ConfigDict(extra="allow")
    
    object: Optional[str] = Field(default="whatsapp_business_account", description="Object type")
    entry: List[WhatsAppEntry] = Field(default_factory=list, description="List of entries")
    
    def get_all_messages(self) -> List[tuple[str, WhatsAppMessage]]:
        """
        Extract all messages with their sender WhatsApp IDs.
        
        Returns:
            List of tuples containing (sender_wa_id, message)
        """
        messages = []
        for entry in self.entry:
            for change in entry.changes:
                if change.field == "messages":
                    sender_wa_id = change.value.get_sender_wa_id()
                    if sender_wa_id:
                        for message in change.value.messages:
                            messages.append((sender_wa_id, message))
        return messages
    
    def get_text_messages(self) -> List[tuple[str, WhatsAppMessage]]:
        """
        Extract all text messages with their sender WhatsApp IDs.
        
        Returns:
            List of tuples containing (sender_wa_id, message)
        """
        messages = []
        for sender_wa_id, message in self.get_all_messages():
            if message.is_text_message():
                messages.append((sender_wa_id, message))
        return messages


# Agent communication models

class AgentMessagePart(BaseModel):
    """Part of an agent message."""
    
    model_config = ConfigDict(extra="forbid")
    
    text: str = Field(..., min_length=1, description="Text content of the message part")


class AgentMessage(BaseModel):
    """Message structure for agent communication."""
    
    model_config = ConfigDict(extra="forbid")
    
    role: Literal["user", "assistant"] = Field(..., description="Message role")
    parts: List[AgentMessagePart] = Field(..., min_items=1, description="Message parts")


class AgentResponse(BaseModel):
    """Response from the agent service."""
    
    model_config = ConfigDict(extra="ignore")  # Allow extra fields from agent
    
    content: Optional[Dict[str, Any]] = Field(default=None, description="Response content")
    
    def extract_text_response(self) -> Optional[str]:
        """
        Extract text response from agent response structure.
        
        Returns:
            Extracted text or None if not found
        """
        if not self.content:
            return None
            
        parts = self.content.get("parts")
        if not isinstance(parts, list) or not parts:
            return None
            
        first_part = parts[0]
        if isinstance(first_part, dict) and "text" in first_part:
            return first_part["text"].strip()
            
        return None


# Outgoing WhatsApp message models

class WhatsAppOutgoingTextBody(BaseModel):
    """Text body for outgoing WhatsApp message."""
    
    model_config = ConfigDict(extra="forbid")
    
    body: str = Field(..., min_length=1, max_length=4096, description="Message text")


class WhatsAppOutgoingMessage(BaseModel):
    """Outgoing message to WhatsApp API."""
    
    model_config = ConfigDict(extra="forbid")
    
    messaging_product: Literal["whatsapp"] = Field(default="whatsapp")
    recipient_type: Literal["individual"] = Field(default="individual")
    to: str = Field(..., description="Recipient phone number")
    type: Literal["text"] = Field(default="text")
    text: WhatsAppOutgoingTextBody = Field(..., description="Text content")
    
    @field_validator('to')
    @classmethod
    def validate_recipient_phone(cls, v: str) -> str:
        """Validate recipient phone number."""
        # Ensure proper format for WhatsApp API
        phone = v.strip()
        if not phone.startswith('+'):
            phone = f'+{phone}'
        return phone


# Processing context models

class MessageProcessingContext(BaseModel):
    """Context for message processing operations."""
    
    model_config = ConfigDict(extra="forbid")
    
    app_name: str = Field(..., min_length=1, description="Application name")
    user_wa_id: str = Field(..., min_length=1, description="User WhatsApp ID")
    session_id: str = Field(..., min_length=1, description="Session ID")
    whatsapp_api_url: str = Field(..., description="WhatsApp API URL")
    wsp_token: str = Field(..., min_length=1, description="WhatsApp token")
    
    @field_validator('whatsapp_api_url')
    @classmethod
    def validate_api_url(cls, v: str) -> str:
        """Validate WhatsApp API URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('WhatsApp API URL must start with http:// or https://')
        return v.rstrip('/')


class AgentRequestPayload(BaseModel):
    """Payload for agent service requests."""
    
    model_config = ConfigDict(extra="forbid")
    
    app_name: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1) 
    session_id: str = Field(..., min_length=1)
    new_message: AgentMessage = Field(...)
    streaming: bool = Field(default=False)
    
    @classmethod
    def create_text_request(
        cls,
        app_name: str,
        user_id: str, 
        session_id: str,
        message_text: str,
        streaming: bool = False
    ) -> "AgentRequestPayload":
        """Create a text message request payload."""
        return cls(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            new_message=AgentMessage(
                role="user",
                parts=[AgentMessagePart(text=message_text)]
            ),
            streaming=streaming
        )
