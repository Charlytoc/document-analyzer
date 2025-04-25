import { useState } from "react";
import { Markdowner } from "../Markdowner/Markdowner";
type TagContent = {
  tag: string;
  content: string;
};

type ExtractedResult = {
  cleanedText: string;
  tagsContent: TagContent[];
};

export function extractContextInsideTags(
  text: string,
  tags: string[]
): ExtractedResult {
  const tagsContent: TagContent[] = [];

  let cleanedText = text;

  for (const tag of tags) {
    const regex = new RegExp(`<${tag}>([\\s\\S]*?)<\\/${tag}>`, "gi");
    let match;

    while ((match = regex.exec(text)) !== null) {
      tagsContent.push({
        tag,
        content: match[1].trim(),
      });

      // Remove match from cleanedText
      cleanedText = cleanedText.replace(match[0], "");
    }
  }

  return {
    cleanedText: cleanedText.trim(),
    tagsContent,
  };
}

export type TMessage = {
  role: "user" | "assistant";
  content: string;
};

export const Message = ({ message }: { message: TMessage }) => {
  const isUser = message.role === "user";

  const { cleanedText, tagsContent } = extractContextInsideTags(
    message.content,
    ["think"]
  );

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
        {tagsContent.map((tag) => (
          <TagRenderer key={tag.tag} {...tag} />
        ))}
        <Markdowner markdown={cleanedText} />
      </div>
    </div>
  );
};

type TagRendererProps = {
  tag: string;
  content: string;
};

export const TagRenderer = ({ tag, content }: TagRendererProps) => {
  const [open, setOpen] = useState(false);

  return (
    <div className="mb-2">
      <button
        onClick={() => setOpen(!open)}
        className="text-xs  hover:underline focus:outline-none border border-gray-300 rounded-md px-2 py-1 cursor-pointer"
      >
        {tag}
        <span>{open ? "▾" : "▸"}</span>
      </button>

      {open && (
        <div className="mt-1 px-2 py-1 text-sm bg-gray-100 border border-gray-300 rounded">
          <Markdowner markdown={content} />
        </div>
      )}
    </div>
  );
};
