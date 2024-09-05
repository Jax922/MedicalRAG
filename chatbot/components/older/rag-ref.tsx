"use client";
import * as React from "react";
import { cn } from "@/lib/utils";
import { useState } from "react";
import { IconArrowElbow } from "@/components/ui/icon";
import { ReferenceItem, Reference } from "@/lib/types";


function RefItem({ referenceItem, index }: { referenceItem: ReferenceItem, index: number }) {
    return (
        <div className={cn("!mt-[1.5rem]")}>
            <p className={cn("text-[1.5rem] leading-tight")}>
                参考[{index+1}]:
                <span className="text-blue-600 ml-2">{referenceItem.title}</span>
            </p>
            {/* 暂时不展示细节 */}
            {/* <div className={cn("text-sm text-gray-700")}>{referenceItem.content}</div> */}
        </div>
    );
}

export default function RagRef({ references }: { references: Reference }) {
    const [isExpanded, setIsExpanded] = useState(true);

    const toggleExpand = () => {
        setIsExpanded(!isExpanded);
    };

    const uniqueReferences = references.filter((reference, index, self) =>
        index === self.findIndex((t) => (
            t.title === reference.title
        ))
    );

    return (
        <div className={cn("p-4 rounded-md shadow-sm border border-gray-500")}>
            <div className={cn("flex justify-between items-center mb-2")}>
                <h3 className={cn("text-[1.5rem] font-semibold")}>健康知识库匹配结果：</h3>
                <button
                    onClick={toggleExpand}
                    className={cn("focus:outline-none text-blue-500 hover:text-blue-600")}
                >
                    {isExpanded ? "▼" : "▲"}
                </button>
            </div>
            {isExpanded && (
                <ul className={cn("list-disc pl-5 space-y-1")}>
                    {uniqueReferences.map((reference, index) => (
                        // <li key={index} className={cn("text-sm text-gray-700")}>
                            <RefItem key={index} referenceItem={reference} index={index}/>
                        // </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
