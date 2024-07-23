"use client";
import * as React from "react";
import { cn } from "@/lib/utils";
import Textarea from 'react-textarea-autosize'
import { IconArrowElbow } from "@/components/ui/icon";
import { SaveAction } from "@/lib/types";

export default function PromptForm({saveAction}: {saveAction: SaveAction}) {
    const [inputValue, setInputValue] = React.useState("");

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
        <form onSubmit={handleSubmit} className="relative flex flex-row items-center justify-between w-full">
            <Textarea
                className="min-h-[30px] w-full resize-none bg-transparent px-5 py-[1.3rem] focus-within:outline-none sm:text-sm border border-gray-300 rounded-lg px-right-12 pr-12"
                placeholder="请描述您的症状、患病时长、检查报告、用药情况等信息"
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
                className={cn(
                    "absolute right-2 top-1/2 transform -translate-y-1/2 p-2 rounded-md",
                    inputValue ? 'bg-blue-500 text-white' : 'bg-gray-300 text-gray-500'
                )}
                disabled={!inputValue.trim()}
            >
                <IconArrowElbow className="w-5 h-5" />
            </button>
        </form>
    )
}