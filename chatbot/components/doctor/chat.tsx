'use client';
import PromptForm from "@/components/prompt-form";
import Message from "@/components/message";
import { saveMessage, fetchMessage, fetchMessageStream } from "@/lib/actions";
import * as Types from "@/lib/types";
import * as React from "react";
import useWebSocket from "@/lib/websocket"
import { isSameMessage } from "@/lib/utils";


export default function Chat() {
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

    const ws = useWebSocket((data) => {
		console.log("Data from websocket:", data);
		console.log(typeof data);
		const message = JSON.parse(data);
		const isHasSameMessage = isSameMessage(message, msgData);
		if (!isHasSameMessage) {
			const newMsgData = [...msgData, message];
			setMsgData(newMsgData);
		}
	})

	React.useEffect(() => {
		if (ws) {
			console.log("Socket is connected and ready to use:", ws);
		} else {
			console.log("Socket is not ready yet.");
		}
	}, [ws]);

	const [msgData, setMsgData] = React.useState<Types.Message[]>(msg);
	const [loading, setLoading] = React.useState(false);

	function saveAction(message: Types.Message) {
		saveMessage(message);
		const newMsgData = [...msgData, message];
		setMsgData(newMsgData);
		console.log("message:", typeof message);
		ws.emit("message", JSON.stringify(message));
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



  return (
    <div className="flex flex-col items-start justify-between h-full">
			<div className="flex flex-col items-start gap-4 p-4 w-full">
				{msgData.map((message) => (
					<Message key={message.id} message={message} />
				))}
			</div>
			<div className="w-full p-4 sticky bottom-0 bg-white">
				<PromptForm saveAction={saveAction} placeholder="请耐心回答问题" isDoctor={true}/>
			</div>
		</div>
  );
}