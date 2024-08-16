import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import * as Types from "@/lib/types"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function isSameMessage(m: Types.Message, ms: Types.Message[]) { 
  return ms.some((msg) => msg.id === m.id)
}