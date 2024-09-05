"use client";
import * as React from "react";
import { cn } from "@/lib/utils";
import Textarea from 'react-textarea-autosize'
import { IconArrowElbow } from "@/components/ui/icon";
import { SaveAction } from "@/lib/types";

export default function PromptForm({saveAction, text}: {saveAction: SaveAction, text: string}) {
    

    const [inputValue, setInputValue] = React.useState(text);

    React.useEffect(() => {
        setInputValue(text);
    }, [text]);

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInputValue(e.target.value);
    }

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (inputValue.trim()) {
            saveAction({
                id: String(Date.now()),
                type: 'user',
                content: inputValue
            });
            setInputValue("");
        }
    }

    return (
        <form onSubmit={handleSubmit} className="relative flex flex-row items-center justify-between w-full"
        >
            <Textarea
                style={{
                }}
                className="!text-[1.7rem] min-h-[60px] w-full resize-none bg-transparent px-5 py-[2rem] focus-within:outline-none sm:text-sm border border-gray-300 rounded-lg px-right-12 pr-[7rem] !leading-tight bg-white"
                placeholder="您有什么想跟我说"  
                minRows={1}
                maxRows={3}
                spellCheck={false}
                autoComplete="off"
                autoCorrect="off"
                value={inputValue}
                onChange={handleInputChange}
            />
            <button
                type="submit"
                onClick={
                    (e) => {
                        // e.preventDefault();

                        //     saveAction({
                        //         id: String(Date.now()),
                        //         type: 'user',
                        //         content: inputValue
                        //     });
                        //     setInputValue("");

                    }
                }
                style={{ fontSize: '1.7rem' }}
                className={cn(
                    "absolute right-6 top-1/2 transform -translate-y-1/2 p-4 rounded-md",
                    inputValue ? 'bg-blue-500 text-white' : 'bg-gray-300 text-gray-500'
                )}
                disabled={!inputValue.trim()}
            >
                {/* <IconArrowElbow style={{ fontSize: '1.25rem' }} className="w-5 h-5" /> */}
                发送
            </button>
        </form>
    )
}