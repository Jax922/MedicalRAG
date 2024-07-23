export type MessageType = "user" | "bot";
export type Message = {
  id: string;
  type: MessageType;
  content: string;
  status?: "sending" | "success" | "error";
};

export type SaveAction = (message: Message) => void;
export type FetchAction = (message: Message) => Promise<Message>;