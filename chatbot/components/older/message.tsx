
import * as React from 'react';
import * as Types from '@/lib/types';
import { IconBot, IconUsers, IconSpeaker } from '@/components/ui/icon';
import { fetchTTSBaidu, fetchTTSXFei } from '@/lib/actions'
import ReactMarkdown from 'react-markdown';
import RagRef from "@/components/older/rag-ref";
import { useSearchParams } from 'next/navigation';


const BotMessage = React.memo(({ message, references }: { message: Types.Message, references?: Types.Reference }) => {
	const searchParams = useSearchParams();
	const Cantonese = searchParams.get('cantonese');
	const isCantonese = Cantonese === 'true';
  
	const [isPlaying, setIsPlaying] = React.useState(false);
	const [audio, setAudio] = React.useState<HTMLAudioElement | null>(null);


	console.log('BotMessage', message.content);
	console.log('BotMessage ref', references);
  
	
  
	const hasFetchedTTS = React.useRef(false);

const fetchTTS = React.useCallback(async () => {
  try {
    if (hasFetchedTTS.current) return;

    hasFetchedTTS.current = true;

    let url = '';

    if (isCantonese) {
      url = await fetchTTSXFei(message.content, "xiaomei");
    } else {
      // url = await fetchTTSBaidu(message.content);
	  url = await fetchTTSXFei(message.content, "xiaoyan");
    }

    const newAudio = new Audio(url);
    setAudio(newAudio);

    newAudio.oncanplaythrough = () => {
      newAudio.play();
      setIsPlaying(true);
    };
    newAudio.onended = () => {
      setIsPlaying(false);
    };
    newAudio.onerror = (err) => {
		alert('Error playing audio');
		alert(err);
      console.error("Error playing audio:", err);
    };

  } catch (error) {
    console.error('Error in TTS process:', error);
  }
}, [isCantonese, message.content]);

React.useEffect(() => {
  if (!audio && !hasFetchedTTS.current) {
    fetchTTS();
  }
  return () => {
    if (audio) {
      audio.pause();
      audio.currentTime = 0;
    }
  };
}, [fetchTTS, audio]);

  
	const handleClick = () => {
	  if (isPlaying && audio) {
		audio.pause();
		setIsPlaying(false);
	  } else if (audio) {
		audio.play();
		setIsPlaying(true);
	  }
	};
  
	return (
	  <div>
		<div className="flex items-start">
		  <div className="flex-shrink-0 bg-white rounded-full flex items-center justify-center mr-2">
			<IconBot className="text-gray-700" />
		  </div>
		  <div className="flex-1 space-x-2 p-4 bg-white rounded-lg shadow-md">
			<ReactMarkdown className="text-[1.7rem] text-gray-800">
			  {message.content}
			</ReactMarkdown>
		  </div>
  
		  {/* TTS 播放按钮 */}
		  <button
			className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ml-2 ${isPlaying ? 'bg-red-600 animate-pulse' : 'bg-green-600 hover:bg-green-700'} focus:ring-green-700`}
			onClick={handleClick}
		  >
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
  
			  {/* 隐藏的 TTS 播放按钮 */}
			  <button className="flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ml-2 bg-green-600 hover:bg-green-700 focus:ring-green-700" onClick={() => {}} style={{
				opacity: 0
			  }}>
				<IconSpeaker className="w-4 h-4" />
			  </button>
			</div>
		  )
		}	
	  </div>
	);
  }, (prevProps, nextProps) => {
	return prevProps.message === nextProps.message && prevProps.references === nextProps.references;
  });



// function BotMessage({ message, references }: { message: Types.Message, references?: Types.Reference }) {

	
//   }

function UserMessage({ message }: { message: Types.Message }) {
  return (
    	<div className="flex items-start">
			<div className="flex-shrink-0  bg_green_default rounded-full flex items-center justify-center mr-2">
				<IconUsers className=" text-blue-700" />
			</div>
			<div className="flex-1 space-x-2 p-4 bg_green_default rounded-lg shadow-md">
				<p className="text-[1.7rem] text-gray-800">{message.content}</p>
			</div>
		</div>
  );
}

export default function Message({ message, references}: { message: Types.Message, references?: Types.Reference }) {
  return message.type === 'bot' ? <BotMessage message={message} references={references}/> : <UserMessage message={message} />;
}