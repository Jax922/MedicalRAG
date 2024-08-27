import React, { useState, useEffect, useRef} from 'react';
import { useSearchParams } from 'next/navigation';
import { FaMicrophone, FaMicrophoneSlash } from 'react-icons/fa';
import { CSSTransition } from 'react-transition-group';
import { fetchASRBaidu } from '@/lib/actions';

const SpeechComponent: React.FC<{ setSpeechText: (text: string) => void }> = ({ setSpeechText }) => {

  const searchParams = useSearchParams();
  const Cantonese = searchParams.get('cantonese');
  const isCantonese = Cantonese === 'true';

  const [transcript, setTranscript] = useState('');
  const [recognition, setRecognition] = useState<SpeechRecognition | null>(null);
  const [listening, setListening] = useState(false);
  const [showHint, setShowHint] = useState(true);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<BlobPart[]>([]);

  // if (!isCantonese) {
    useEffect(() => {
      if (!('SpeechRecognition' in window) && !('webkitSpeechRecognition' in window)) {
        console.log('浏览器不支持语音识别');
        return;
      }
  
      const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      if (!isCantonese) {
        recognitionInstance.lang = 'zh-CN';
      } else {
        recognitionInstance.lang = 'zh-HK';
      }
      
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = false;
  
      recognitionInstance.onresult = (event: SpeechRecognitionEvent) => {
        setShowHint(false);
        setTranscript(event.results[0][0].transcript);
        setSpeechText(event.results[0][0].transcript);
      };
  
      setRecognition(recognitionInstance);
    }, [setSpeechText]);
  // }
  function googleASR() {
    if (recognition) {
      if (listening) {
        recognition.stop();
      } else {
        recognition.start();
        setShowHint(true); // 开始录音时显示提示
      }
      setListening(!listening);
    }
  }


  const toggleListening = () => {
    googleASR();
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      <CSSTransition
        in={showHint}
        timeout={500}
        classNames="hint"
        unmountOnExit
      >
        <div className="text-[1.5rem] p-4 text-center bg-yellow-100 border border-yellow-300 rounded-md">
          {listening ? '录音中... 点击按钮可以暂停录音' : '点击按钮开始语音输入'}
        </div>
      </CSSTransition>
      <button 
        onClick={toggleListening} 
        className={`flex items-center justify-center w-24 h-24 text-3xl text-white rounded-full focus:outline-none focus:ring-2 ${listening ? 'bg-red-600 hover:bg-red-700 focus:ring-red-700' : 'bg-green-600 hover:bg-green-700 focus:ring-green-700'}`}
      >
        {listening ? <FaMicrophone className="animate-pulse" /> : <FaMicrophone />}
      </button>
      <br />
      {/* <p className="text-lg">{transcript}</p>  */}
      {/* 这一行用于语音调试 */}
    </div>
  );
};

export default SpeechComponent;