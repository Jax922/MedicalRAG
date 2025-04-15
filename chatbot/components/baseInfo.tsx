'use client';
import { useState } from 'react';

export default function BasicInfo({ phone, onSubmit }: { phone: string, onSubmit: () => void }) {
  const [formData, setFormData] = useState({
    name: '', gender: '', birthday: '', height: '', weight: '',
    bloodPressure: '', bloodSugar: '', chronic: '', medication: '', avoid: ''
  });

  const handleSubmit = async () => {
    await fetch('/api/submit-info', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, ...formData })
    });
    onSubmit();
  };

  const update = (field: string, val: string) => setFormData({ ...formData, [field]: val });

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-center">Complete Your Profile</h2>
      {['name', 'gender', 'birthday', 'height', 'weight', 'bloodPressure', 'bloodSugar', 'chronic', 'medication', 'avoid'].map((field) => (
        <input
          key={field}
          type="text"
          placeholder={field.charAt(0).toUpperCase() + field.slice(1)}
          value={(formData as any)[field]}
          onChange={(e) => update(field, e.target.value)}
          className="w-full border rounded px-4 py-2"
        />
      ))}
      <button
        onClick={handleSubmit}
        className="w-full bg-green-600 text-white py-2 rounded text-lg"
      >
        Submit Info
      </button>
    </div>
  );
}