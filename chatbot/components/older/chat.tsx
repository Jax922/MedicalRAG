'use client';
import { useSearchParams } from 'next/navigation';
import OlderPromptForm from "@/components/older/prompt-form";
import OldMessage from "@/components/older/message";
import RagRef from "@/components/older/rag-ref";
import { saveMessage, fetchMessage, fetchMessageStream, fetchMessageStreamDify, fetchMessageLocal, fetchRAGLocal, fetchResetHistory } from "@/lib/actions";
import useWebSocket from "@/lib/websocket"
import SpeechToText from "@/components/older/speech";
import * as Types from "@/lib/types";
import * as React from "react";
import { isSameMessage } from '@/lib/utils';



export default function Chat() {

	const searchParams = useSearchParams();
  	const doctor = searchParams.get('doctor'); 
	const defaultKeywordString = "高血压,高血压病,冠心病,心脏病,心力衰竭,心衰,心力不足,动脉粥样硬化,动脉硬化,血管硬化,糖尿病,血糖高,慢性阻塞性肺疾病,慢性支气管炎,肺气肿,哮喘,喘息病,肺炎,肺部感染,阿尔茨海默病,老年痴呆,痴呆症,前列腺增生,前列腺肥大,前列腺问题,尿失禁,尿漏,尿路感染,尿道炎"
	const defaultKeywords = defaultKeywordString.split(',');
	const [selectedOption, setSelectedOption] = React.useState("keyword");
	const [keywords, setKeywords] = React.useState(defaultKeywords);


	const isDoctor = doctor === 'true';

	if (isDoctor) {
		const ws = useWebSocket((data) => {
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
	}


	if (!isDoctor) {

		React.useEffect(() => {
			async function fetchSettings() {
			  try {
				const response = await fetch('/api/setting', {
				  method: 'GET',
				  headers: {
					'Content-Type': 'application/json',
				  },
				});
				if (!response.ok) {
				  throw new Error('网络响应不是 OK');
				}
				const data = await response.json();
				setSelectedOption(data.option || 'keyword');
				setKeywords(data.keywords.split(',') || []);
			  } catch (error) {
				// setError(error.message);
			  } finally {
				// setLoading(false);
			  }
			}
			fetchSettings();
		  }, []); 

	}




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

		if (isDoctor) {
			sendMsg2Doctor(message);
			return;
		}

		// fetchAction(newMsgData);
		// fetchActionStream(newMsgData);
		// fetchActionDify(newMsgData);
		// fetchActionStreamDify(newMsgData);

		if (selectedOption === 'keyword') {
			console.log('keywords fetch');
			if (keywords.some((keyword) => message.content.includes(keyword))) {
				console.log('rag fetch');
				fetchResetHistory();
				fetchRAG(newMsgData);
			} else {
				console.log('non-rag fetch');
				fetchActionLocal(newMsgData);
			}
			return;
		}

		if (selectedOption === 'all') {
			console.log('all rag fetch');
			console.log('rag fetch');
			fetchResetHistory();
			fetchRAG(newMsgData);
			return;
		}

		if (selectedOption === 'none') {
			console.log('none rag fetch');
			console.log('non-rag fetch');
			fetchActionLocal(newMsgData);
			return
		}

		// fetchActionLocal(newMsgData);
		
	}

	function sendMsg2Doctor(message: Types.Message) {
		ws.emit('message', JSON.stringify(message));
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
	

	async function fetchRAG(msgData: Types.Message[]) {
		// fetchRAGLocal
		setLoading(true);
		
		try {
			const message = await fetchRAGLocal(msgData);
	
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


  return (
    <div className="flex flex-col items-start justify-between h-full">
			<div className="flex flex-col items-start gap-4 p-4 w-full">
				{msgData.map((message) => (
					<OldMessage key={message.id} message={message} references={message.references}/>
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