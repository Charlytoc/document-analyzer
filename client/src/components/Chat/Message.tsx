import { Markdowner } from "../Markdowner/Markdowner";

export type TMessage = {
  role: "user" | "assistant";
  content: string;
};

export const Message = ({ message }: { message: TMessage }) => {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} `}>
      <div
        className={`
          max-w-lg px-4 py-2 rounded-lg 
          ${
            isUser
              ? "bg-edomex text-white rounded-br-none"
              : "bg-gray-200 text-gray-800 rounded-bl-none"
          }
        `}
      >
        <Markdowner markdown={message.content} />
      </div>
    </div>
  );
};
