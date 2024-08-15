'use client';
import OlderPromptForm from "@/components/older/prompt-form";
import OldMessage from "@/components/older/message";
import { saveMessage, fetchMessage, fetchMessageStream, fetchMessageStreamDify, fetchMessageLocal, fetchRAGLocal } from "@/lib/actions";
import SpeechToText from "@/components/older/speech";
import * as Types from "@/lib/types";
import * as React from "react";


export default function Chat() {

	const [speechText, setSpeechText] = React.useState("");

	const msg: Types.Message[] = [
		// {
		// 	id: '1',
		// 	type: 'user',
		// 	content: '你好，我感觉不舒服。'
		// },
		// {
		// 	id: '2',
		// 	type: 'bot',
		// 	content: '很抱歉听到这个消息。请问您有什么具体的症状？'
		// }
	];

	const [msgData, setMsgData] = React.useState<Types.Message[]>(msg);
	const [loading, setLoading] = React.useState(false);

	const onSpeechChange = (text: string) => {
		setSpeechText(text);
	}

	function saveAction(message: Types.Message) {
		saveMessage(message);
		const newMsgData = [...msgData, message];
		console.log('newMsgData:', newMsgData);
		setMsgData(newMsgData);
		// fetchAction(newMsgData);
		// fetchActionStream(newMsgData);
		// fetchActionDify(newMsgData);
		// fetchActionStreamDify(newMsgData);

		fetchActionLocal(newMsgData);
		fetchRAG(newMsgData);
		
	}

	function fetchAction(msgData: Types.Message[]) {
		setLoading(true);
		fetchMessage(msgData)
			.then((message) => {
				const newMsgData = [...msgData, message];
				console.log('newMsgData:', newMsgData);
				setMsgData(newMsgData);
			})
			.catch((error) => {
				console.error("Error fetching message:", error);
			})
			.finally(() => {
				setLoading(false);
			});
	}

	async function fetchActionStream(msgData: Types.Message[]) {
		setLoading(true);

		const botMessage: Types.Message = {
				id: String(Date.now()),
				type: 'bot',
				content: ''
		};

		setMsgData(prev => [...prev, botMessage]);

		try {
				for await (const chunk of fetchMessageStream(msgData)) {
						setMsgData(prev => {
								const updatedMessages = [...prev];
								updatedMessages[updatedMessages.length - 1].content += chunk;
								return updatedMessages;
						});
				}
		} catch (error) {
				console.error("Error fetching message:", error);
		} finally {
				setLoading(false);
		}
	}

	async function fetchActionDify(msgData: Types.Message[]) {
		setLoading(true);
	
		const botMessage: Types.Message = {
			id: String(Date.now()),
			type: 'bot',
			content: ''
		};
	
		// setMsgData(prev => [...prev, botMessage]);
	
		try {
			const message = await fetchMessage(msgData);
	
			setMsgData(prev => {
				const updatedMessages = [...prev];
				updatedMessages.push(message);
				return updatedMessages;
			});
		} catch (error) {
			console.error("Error fetching message:", error);
		} finally {
			setLoading(false)
		}
	}

	async function fetchActionLocal(msgData: Types.Message[]) {
		setLoading(true);
	
		try {
			const message = await fetchMessageLocal(msgData);
	
			setMsgData(prev => {
				const updatedMessages = [...prev];
				updatedMessages.push(message);
				return updatedMessages;
			});

			console.log('msgData:', msgData);

		} catch (error) {
			console.error("Error fetching message:", error);
		} finally {
			setLoading(false)
		}
	}

	async function fetchActionStreamDify(msgData: Types.Message[]) {
		setLoading(true);
	
		const botMessage: Types.Message = {
			id: String(Date.now()),
			type: 'bot',
			content: ''
		};
	
		setMsgData(prev => [...prev, botMessage]);
	
		try {
			for await (const chunk of fetchMessageStreamDify(msgData)) {
				console.log("Received chunk:", chunk);
	
				setMsgData(prev => {
					const updatedMessages = [...prev];
					const currentContent = updatedMessages[updatedMessages.length - 1].content;
	
					// 删除重复的chunk，这里不知道是否放到后端api更好？
					if (!currentContent.endsWith(chunk)) {
						updatedMessages[updatedMessages.length - 1].content += chunk;
					}
					
					return updatedMessages;
				});
			}
		} catch (error) {
			console.error("Error fetching message:", error);
		} finally {
			setLoading(false);
		}
	}	
	

	function fetchRAG(msgData: Types.Message[]) {
		// fetchRAGLocal
		setLoading(true);
		
		fetchRAGLocal(msgData)
	}


  return (
    <div className="flex flex-col items-start justify-between h-full">
			<div className="flex flex-col items-start gap-4 p-4 w-full">
				{msgData.map((message) => (
					<OldMessage key={message.id} message={message} />
				))}
			</div>
			{	loading &&
				<div className="loading-spinner">
            		<div className="spinner"></div>
        		</div>
			}
			<div className="w-full p-4 sticky bottom-0 bg-white">
				<SpeechToText setSpeechText={onSpeechChange}/>
				<OlderPromptForm saveAction={saveAction} text={speechText}/>
			</div>
		</div>
  );
}