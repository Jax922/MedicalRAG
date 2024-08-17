import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import * as Types from "@/lib/types"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// [[string, string]] to [{title: string, content: string}]
export function toReference(data: [string, string][]): Types.Reference {
  return data.map(([content, title]) => ({ title, content }))
}

export function isSameMessage(m: Types.Message, ms: Types.Message[]) { 
  return ms.some((msg) => msg.id === m.id)
}