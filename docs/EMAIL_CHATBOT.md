# Email Chatbot

## Workflow
1. When user emails arrive, create an `EmailConversation` with subject and user email
2. Store the original user message as a `ChatMessage` with role=USER
3. Store AI responses as `ChatMessage` with role=ASSISTANT
4. Messages are linked by `email_conversation_id` and ordered by `created_at`

## Database Tables

### 1. EmailConversation
**Purpose**: Groups related emails and chat messages together as conversation threads.

**Essential Fields**:
- `id` (UUID, primary key)
- `subject` (string, email subject)
- `user_email` (string, indexed for quick lookup)
- `created_at` and `updated_at` (timestamps)

**Relationships**:
- One-to-many with ChatMessage

### 2. ChatMessage
**Purpose**: Stores individual messages within a conversation (both user and AI responses).

**Essential Fields**:
- `id` (UUID, primary key)
- `email_conversation_id` (UUID, foreign key)
- `role` (enum: USER or ASSISTANT)
- `content` (text, message content)
- `created_at` (timestamp)

**Relationships**:
- Many-to-one with EmailConversation
