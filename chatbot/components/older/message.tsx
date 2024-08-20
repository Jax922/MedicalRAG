
import * as React from 'react';
import * as Types from '@/lib/types';
import { IconBot, IconUsers, IconSpeaker } from '@/components/ui/icon';
import { fetchTTSBaidu } from '@/lib/actions'
import ReactMarkdown from 'react-markdown';
import RagRef from "@/components/older/rag-ref";

function BotMessage({ message, references }: { message: Types.Message, references?: Types.Reference }) {

	// click button to support TTS
	const handleClick = () => {
		// const utterance = new SpeechSynthesisUtterance(message.content);
		// utterance.lang = 'zh-CN';
		// speechSynthesis.speak(utterance);
		fetchTTS();
	}

	// fetch TTS from Baidu
	const fetchTTS = async () => {
		try {
			const url = await fetchTTSBaidu(message.content);
			console.log(url);
	
			const audio = new Audio(url);
			audio.oncanplaythrough = () => {
				audio.play();
			};
			audio.onerror = (err) => {
				console.error("Error playing audio:", err);
			};
		} catch (error) {
			console.error('Error in TTS process:', error);
		}
	}

  return (
	<div>
		<div className="flex items-start">
				<div className="flex-shrink-0 bg-gray-300 rounded-full flex items-center justify-center mr-2">
					<IconBot className="text-gray-700" />
				</div>
				<div className="flex-1 space-x-2 p-4 bg-gray-100 rounded-lg shadow-md">
					<ReactMarkdown className="text-[2.5rem] text-gray-800">
						{message.content}
					</ReactMarkdown>
				</div>
				
				
				{/* add click button to support TTS */}
				<button className="flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ml-2  bg-green-600 hover:bg-green-700 focus:ring-green-700" onClick={handleClick}>
					<IconSpeaker className="w-4 h-4" />
				</button>
		</div>
		{
			references && references.length > 0 && (
				<div className="flex items-start text-lg mt-3">
					<div className="flex-shrink-0 w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center mr-2" style={{
							opacity: 0
						}}>
						<IconBot className="w-6 h-6 text-gray-700" style={{
							opacity: 0
						}}/>
					</div>
					<div className="flex-1 space-x-2 rounded-lg shadow-md">
						<RagRef references={references} />
					</div>
					
					
					{/* add click button to support TTS */}
					<button className="flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ml-2  bg-green-600 hover:bg-green-700 focus:ring-green-700" onClick={()=>{}} style={{
							opacity: 0
						}}>
						<IconSpeaker className="w-4 h-4" />
					</button>
				</div>
			)
		}	
	</div>
  );
}

function UserMessage({ message }: { message: Types.Message }) {
  return (
    	<div className="flex items-start">
			<div className="flex-shrink-0  bg-blue-300 rounded-full flex items-center justify-center mr-2">
				<IconUsers className=" text-blue-700" />
			</div>
			<div className="flex-1 space-x-2 p-4 bg-blue-100 rounded-lg shadow-md">
				<p className="text-[2.5rem] text-gray-800">{message.content}</p>
			</div>
		</div>
  );
}

export default function Message({ message, references}: { message: Types.Message, references?: Types.Reference }) {
  return message.type === 'bot' ? <BotMessage message={message} references={references}/> : <UserMessage message={message} />;
}