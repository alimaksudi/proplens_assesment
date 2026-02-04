# assistant-ui

> React components for AI chat interfaces

## Table of Contents

### architecture

- [Architecture](https://www.assistant-ui.com/docs/architecture): How components, runtimes, and cloud services fit together.

### cli

- [CLI](https://www.assistant-ui.com/docs/cli): Scaffold projects, add components, and manage updates from the command line.

### devtools

- [DevTools](https://www.assistant-ui.com/docs/devtools): Inspect runtime state, context, and events in the browser.

### root

- [Introduction](https://www.assistant-ui.com/docs): Beautiful, enterprise-grade AI chat interfaces for React applications.

### installation

- [Installation](https://www.assistant-ui.com/docs/installation): Get assistant-ui running in 5 minutes with npm and your first chat component.

### llm

- [AI-Assisted Development](https://www.assistant-ui.com/docs/llm): Use AI tools to build with assistant-ui faster. AI-accessible documentation, Claude Code skills, and MCP integration.

### react-compatibility

- [Using old React versions](https://www.assistant-ui.com/docs/react-compatibility): Compatibility notes for React 18, 17, and 16.

### runtimes

- [Assistant Transport](https://www.assistant-ui.com/docs/runtimes/assistant-transport): Stream agent state to the frontend and handle user commands for custom agents.
- [Data Stream Protocol](https://www.assistant-ui.com/docs/runtimes/data-stream): Integration with data stream protocol endpoints for streaming AI responses.
- [Helicone](https://www.assistant-ui.com/docs/runtimes/helicone): Configure Helicone proxy for OpenAI API logging and monitoring.
- [LangChain LangServe](https://www.assistant-ui.com/docs/runtimes/langserve): Connect to LangServe endpoints via Vercel AI SDK integration.
- [Picking a Runtime](https://www.assistant-ui.com/docs/runtimes/pick-a-runtime): Which runtime fits your backend? Decision guide for common setups.
- [AI SDK v4 (Legacy)](https://www.assistant-ui.com/docs/runtimes/ai-sdk/v4-legacy): Legacy integration for Vercel AI SDK v4 using data stream runtime.
- [AI SDK v5 (Legacy)](https://www.assistant-ui.com/docs/runtimes/ai-sdk/v5-legacy): Integrate Vercel AI SDK v5 with useChatRuntime for streaming chat.
- [AI SDK v6](https://www.assistant-ui.com/docs/runtimes/ai-sdk/v6): Integrate Vercel AI SDK v6 with assistant-ui for streaming chat.
- [Custom Thread List](https://www.assistant-ui.com/docs/runtimes/custom/custom-thread-list): Plug a custom thread database for multi-thread persistence.
- [ExternalStoreRuntime](https://www.assistant-ui.com/docs/runtimes/custom/external-store): Bring your own Redux, Zustand, or state manager.
- [LocalRuntime](https://www.assistant-ui.com/docs/runtimes/custom/local): Quickest path to a working chat. Handles state while you handle the API.
- [Getting Started](https://www.assistant-ui.com/docs/runtimes/langgraph): Connect to LangGraph Cloud API for agent workflows with streaming.
- [Full-Stack Integration](https://www.assistant-ui.com/docs/runtimes/mastra/full-stack-integration): Integrate Mastra directly into Next.js API routes.
- [Overview](https://www.assistant-ui.com/docs/runtimes/mastra/overview): TypeScript agent framework for AI applications with tools and workflows.
- [Separate Server Integration](https://www.assistant-ui.com/docs/runtimes/mastra/separate-server-integration): Run Mastra as a standalone server connected to your frontend.
- [Introduction](https://www.assistant-ui.com/docs/runtimes/langgraph/tutorial): Build a stockbroker assistant with LangGraph and assistant-ui.
- [Introduction](https://www.assistant-ui.com/docs/runtimes/langgraph/tutorial/introduction): Build a stockbroker assistant with LangGraph and assistant-ui.
- [Part 1: Setup frontend](https://www.assistant-ui.com/docs/runtimes/langgraph/tutorial/part-1): Create a Next.js project with the LangGraph assistant-ui template.
- [Part 2: Generative UI](https://www.assistant-ui.com/docs/runtimes/langgraph/tutorial/part-2): Display stock ticker information with generative UI components.
- [Part 3: Approval UI](https://www.assistant-ui.com/docs/runtimes/langgraph/tutorial/part-3): Add human-in-the-loop approval for tool calls.

### ui

- [Accordion](https://www.assistant-ui.com/docs/ui/accordion): A vertically stacked set of interactive headings that reveal or hide content sections.
- [AssistantModal](https://www.assistant-ui.com/docs/ui/assistant-modal): Floating chat bubble for support widgets and help desks.
- [AssistantSidebar](https://www.assistant-ui.com/docs/ui/assistant-sidebar): Side panel chat for co-pilot experiences and inline assistance.
- [Attachment](https://www.assistant-ui.com/docs/ui/attachment): UI components for attaching and viewing files in messages.
- [Badge](https://www.assistant-ui.com/docs/ui/badge): A small label component for displaying status, categories, or metadata.
- [Diff Viewer](https://www.assistant-ui.com/docs/ui/diff-viewer): Render code diffs with syntax highlighting for additions and deletions.
- [File](https://www.assistant-ui.com/docs/ui/file): Display file message parts with icon, name, size, and download button.
- [Image](https://www.assistant-ui.com/docs/ui/image): Display image message parts with preview, loading states, and fullscreen dialog.
- [Markdown](https://www.assistant-ui.com/docs/ui/markdown): Display rich text with headings, lists, links, and code blocks.
- [Mermaid Diagrams](https://www.assistant-ui.com/docs/ui/mermaid): Render Mermaid diagrams in chat messages with streaming support.
- [ModelSelector](https://www.assistant-ui.com/docs/ui/model-selector): Model picker with unified overlay positioning and runtime integration.
- [Message Part Grouping](https://www.assistant-ui.com/docs/ui/part-grouping): Organize message parts into custom groups with flexible grouping functions.
- [Reasoning](https://www.assistant-ui.com/docs/ui/reasoning): Collapsible UI for displaying AI reasoning and thinking messages.
- [Custom Scrollbar](https://www.assistant-ui.com/docs/ui/scrollbar): Replace the default scrollbar with a custom Radix UI scroll area.
- [Select](https://www.assistant-ui.com/docs/ui/select): A dropdown select component with composable sub-components.
- [Sources](https://www.assistant-ui.com/docs/ui/sources): Display URL sources with favicon, title, and external link.
- [Streamdown](https://www.assistant-ui.com/docs/ui/streamdown): Alternative markdown renderer with built-in syntax highlighting, math, and diagram support.
- [Syntax Highlighting](https://www.assistant-ui.com/docs/ui/syntax-highlighting): Code block syntax highlighting with react-shiki or react-syntax-highlighter.
- [Tabs](https://www.assistant-ui.com/docs/ui/tabs): A multi-variant tabs component for organizing content into switchable panels.
- [ThreadList](https://www.assistant-ui.com/docs/ui/thread-list): Switch between conversations. Supports sidebar or dropdown layouts.
- [Thread](https://www.assistant-ui.com/docs/ui/thread): The main chat container with messages, composer, and auto-scroll.
- [ToolFallback](https://www.assistant-ui.com/docs/ui/tool-fallback): Default UI component for tools without dedicated custom renderers.
- [ToolGroup](https://www.assistant-ui.com/docs/ui/tool-group): Wrapper for consecutive tool calls with collapsible and styled options.

### copilots

- [Assistant Frame API](https://www.assistant-ui.com/docs/copilots/assistant-frame): Share model context across iframe boundaries
- [makeAssistantVisible](https://www.assistant-ui.com/docs/copilots/make-assistant-readable): Make React components visible and interactive to assistants via higher-order component wrapping.
- [makeAssistantToolUI](https://www.assistant-ui.com/docs/copilots/make-assistant-tool-ui): Register custom UI components to render tool executions and their status.
- [makeAssistantTool](https://www.assistant-ui.com/docs/copilots/make-assistant-tool): Create React components that provide reusable tools to the assistant.
- [Model Context](https://www.assistant-ui.com/docs/copilots/model-context): Configure assistant behavior through system instructions, tools, and context providers.
- [Intelligent Components](https://www.assistant-ui.com/docs/copilots/motivation): Add intelligence to React components through readable interfaces and assistant tools.
- [useAssistantInstructions](https://www.assistant-ui.com/docs/copilots/use-assistant-instructions): React hook for setting system instructions to guide assistant behavior.

### guides

- [Attachments](https://www.assistant-ui.com/docs/guides/attachments): Let users attach files, images, and documents to messages.
- [Message Branching](https://www.assistant-ui.com/docs/guides/branching): Navigate between different conversation branches when editing or reloading messages.
- [Context API](https://www.assistant-ui.com/docs/guides/context-api): Read and update assistant state to build custom components.
- [Speech-to-Text (Dictation)](https://www.assistant-ui.com/docs/guides/dictation): 
- [Message Editing](https://www.assistant-ui.com/docs/guides/editing): Allow users to edit their messages with custom editor interfaces.
- [LaTeX](https://www.assistant-ui.com/docs/guides/latex): Render mathematical expressions in chat messages using KaTeX.
- [Text-to-Speech (Speech Synthesis)](https://www.assistant-ui.com/docs/guides/speech): Read messages aloud with Web Speech API or custom TTS.
- [Suggestions](https://www.assistant-ui.com/docs/guides/suggestions): Display suggested prompts to help users get started with your assistant.
- [Generative UI](https://www.assistant-ui.com/docs/guides/tool-ui): Render tool calls as interactive UI instead of plain text.
- [Tools](https://www.assistant-ui.com/docs/guides/tools): Give your assistant actions like API calls, database queries, and more.

### api-reference

- [Overview](https://www.assistant-ui.com/docs/api-reference/overview): API reference for primitives, runtime hooks, and context providers.
- [<AssistantRuntimeProvider />](https://www.assistant-ui.com/docs/api-reference/context-providers/assistant-runtime-provider): Root provider that connects your runtime to assistant-ui components.
- [<TextMessagePartProvider />](https://www.assistant-ui.com/docs/api-reference/context-providers/text-message-part-provider): Context provider for reusing text components outside of message content.
- [@assistant-ui/react-data-stream](https://www.assistant-ui.com/docs/api-reference/integrations/react-data-stream): Hooks for connecting to data stream protocol endpoints and Assistant Cloud.
- [@assistant-ui/react-hook-form](https://www.assistant-ui.com/docs/api-reference/integrations/react-hook-form): React Hook Form integration for AI-assisted form filling.
- [@assistant-ui/react-ai-sdk](https://www.assistant-ui.com/docs/api-reference/integrations/vercel-ai-sdk): Vercel AI SDK v5 integration with chat runtime hooks and transport utilities.
- [ActionBarMorePrimitive](https://www.assistant-ui.com/docs/api-reference/primitives/action-bar-more): 
- [ActionBarPrimitive](https://www.assistant-ui.com/docs/api-reference/primitives/action-bar): Buttons for message actions like copy, edit, reload, speak, and feedback.
- [AuiIf](https://www.assistant-ui.com/docs/api-reference/primitives/assistant-if): Conditional rendering component based on thread, message, or composer state.
- [AssistantModalPrimitive](https://www.assistant-ui.com/docs/api-reference/primitives/assistant-modal): A popover chat interface for floating assistant UI in the corner of the screen.
- [AttachmentPrimitive](https://www.assistant-ui.com/docs/api-reference/primitives/attachment): Components for displaying and managing file attachments in messages and composer.
- [BranchPickerPrimitive](https://www.assistant-ui.com/docs/api-reference/primitives/branch-picker): Navigate between conversation branches with previous/next controls.
- [ComposerPrimitive](https://www.assistant-ui.com/docs/api-reference/primitives/composer): Primitives for the text input, send button, and attachments.
- [Composition](https://www.assistant-ui.com/docs/api-reference/primitives/composition): How to compose primitives with custom components using asChild.
- [ErrorPrimitive](https://www.assistant-ui.com/docs/api-reference/primitives/error): Components for displaying error messages in the chat interface.
- [MessagePartPrimitive](https://www.assistant-ui.com/docs/api-reference/primitives/message-part): Primitives for text, images, tool calls, and other message content.
- [MessagePrimitive](https://www.assistant-ui.com/docs/api-reference/primitives/message): Components for rendering message content, parts, and attachments.
- [SuggestionPrimitive](https://www.assistant-ui.com/docs/api-reference/primitives/suggestion): 
- [ThreadListItemMorePrimitive](https://www.assistant-ui.com/docs/api-reference/primitives/thread-list-item-more): Dropdown menu for additional thread actions like archive and delete.
- [ThreadListItemPrimitive](https://www.assistant-ui.com/docs/api-reference/primitives/thread-list-item): Individual thread item with title, archive, and delete controls.
- [ThreadListPrimitive](https://www.assistant-ui.com/docs/api-reference/primitives/thread-list): Display and manage multiple conversation threads with create and archive actions.
- [ThreadPrimitive](https://www.assistant-ui.com/docs/api-reference/primitives/thread): Primitives for the message list, viewport, and welcome screen.
- [AssistantRuntime](https://www.assistant-ui.com/docs/api-reference/runtimes/assistant-runtime): Root runtime for managing threads, tool UIs, and assistant state.
- [AttachmentRuntime](https://www.assistant-ui.com/docs/api-reference/runtimes/attachment-runtime): Hooks for accessing attachment state in composer and messages.
- [ComposerRuntime](https://www.assistant-ui.com/docs/api-reference/runtimes/composer-runtime): Runtime for programmatically controlling the message composer.
- [MessagePartRuntime](https://www.assistant-ui.com/docs/api-reference/runtimes/message-part-runtime): Hook for accessing message part state within parts.
- [MessageRuntime](https://www.assistant-ui.com/docs/api-reference/runtimes/message-runtime): Hooks for accessing message state, utilities, and edit composer.
- [ThreadListItemRuntime](https://www.assistant-ui.com/docs/api-reference/runtimes/thread-list-item-runtime): Runtime for managing individual thread list items.
- [ThreadListRuntime](https://www.assistant-ui.com/docs/api-reference/runtimes/thread-list-runtime): Runtime for accessing and managing the list of threads.
- [ThreadRuntime](https://www.assistant-ui.com/docs/api-reference/runtimes/thread-runtime): Runtime for thread state, messages, and viewport management.