
import * as React from 'react';
import * as Types from '@/lib/types';
import { IconBot, IconUsers } from '@/components/ui/icon';
function BotMessage({ message }: { message: Types.Message }) {
  return (
    <div className="flex items-start">
			<div className="flex-shrink-0 w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center mr-2">
				<IconBot className="w-6 h-6 text-gray-700" />
			</div>
			<div className="flex-1 space-x-2 p-2 bg-gray-100 rounded-lg shadow-md">
				<p className="text-sm text-gray-800">{message.content}</p>
			</div>
	</div>
  );
}

function UserMessage({ message }: { message: Types.Message }) {
  return (
    <div className="flex items-start">
			<div className="flex-shrink-0 w-6 h-6 bg-blue-300 rounded-full flex items-center justify-center mr-2">
				<IconUsers className="w-6 h-6 text-blue-700" />
			</div>
			<div className="flex-1 space-x-2 p-2 bg-blue-100 rounded-lg shadow-md">
				<p className="text-sm text-gray-800">{message.content}</p>
			</div>
		</div>
  );
}

export default function Message({ message }: { message: Types.Message }) {
  return message.type === 'bot' ? <BotMessage message={message} /> : <UserMessage message={message} />;
}