'use client';
import { useState } from 'react';
import { Tabs, Picker, TextArea, Button, Toast } from 'antd-mobile';
import { API_BASE } from '@/lib/config';


export default function BasicInfo({ phone, onSubmit }: { phone: string, onSubmit: () => void }) {
  const [formData, setFormData] = useState({
    gender: '', age: '', height: '', weight: '',
    bloodPressure: '', bloodSugar: '', chronic: '', medication: '', avoid: ''
  });

  const [tabKey, setTabKey] = useState('1');

  const update = (field: string, val: string | null) =>
    setFormData({ ...formData, [field]: val ?? '' });

  const handleSubmit = async () => {
    await fetch(`${API_BASE}/api/submit-info`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, ...formData })
    });

    Toast.show({ icon: 'success', content: '信息提交成功' });

    onSubmit();
  };

  const ageOptions = Array.from({ length: 21 }, (_, i) => {
    const age = 60 + i;
    return { label: `${age}岁`, value: `${age}` };
  });

  const validateAndNext = () => {
    const { gender, age, height, weight } = formData;
    if (!gender || !age || !height || !weight) {
      Toast.show({ icon: 'fail', content: '请填写完整的必填信息' });
      return;
    }
    setTabKey('2');
  };

  return (
    <Tabs activeKey={tabKey} onChange={setTabKey} className="text-2xl --title-font-size" style={{ '--title-font-size': '24px' }}>
      <Tabs.Tab title='基本信息' key='1' className='text-2xl'>
        <div className='p-4 space-y-4 text-2xl'>
          <Picker columns={[[{ label: '男', value: '男' }, { label: '女', value: '女' }]]} onConfirm={(val) => update('gender', val[0])}>
            {(items, { open }) => (
              <div onClick={open} className='border p-3 rounded cursor-pointer bg-white'>
                性别：{items.length > 0 ? items.map(i => i?.label).join('') : '请选择'}
              </div>
            )}
          </Picker>

          <Picker columns={[ageOptions]} onConfirm={(val) => update('age', val[0])}>
            {(items, { open }) => (
              <div onClick={open} className='border p-3 rounded cursor-pointer bg-white'>
                年龄：{items.length > 0 ? items.map(i => i?.label).join('') : '请选择'}
              </div>
            )}
          </Picker>

          <Picker
            columns={[[
              { label: '＜150cm', value: '＜150cm' },
              { label: '150-159cm', value: '150-159cm' },
              { label: '160-169cm', value: '160-169cm' },
              { label: '170-179cm', value: '170-179cm' },
              { label: '＞180cm', value: '＞180cm' },
            ]]} onConfirm={(val) => update('height', val[0])}>
            {(items, { open }) => (
              <div onClick={open} className='border p-3 rounded cursor-pointer bg-white'>
                身高：{items.length > 0 ? items.map(i => i?.label).join('') : '请选择'}
              </div>
            )}
          </Picker>

          <Picker
            columns={[[
              { label: '＜45kg', value: '＜45kg' },
              { label: '45-59kg', value: '45-59kg' },
              { label: '60-74kg', value: '60-74kg' },
              { label: '75-89kg', value: '75-89kg' },
              { label: '＞90kg', value: '＞90kg' },
            ]]} onConfirm={(val) => update('weight', val[0])}>
            {(items, { open }) => (
              <div onClick={open} className='border p-3 rounded cursor-pointer bg-white'>
                体重：{items.length > 0 ? items.map(i => i?.label).join('') : '请选择'}
              </div>
            )}
          </Picker>

          <Button color='primary' size='large' block onClick={validateAndNext}>
            下一步
          </Button>
        </div>
      </Tabs.Tab>

      <Tabs.Tab title='健康详情' key='2'>
        {/* 提示这部分选填 */}
        <div className="text-gray-500 text-xl mb-2">提示：此部分为选填，如有请填写~</div>

        <div className='p-4 space-y-4 text-2xl'>
          <Picker
            columns={[[
              { label: '正常', value: '正常' },
              { label: '偏高', value: '偏高' },
              { label: '偏低', value: '偏低' },
              { label: '不确定', value: '不确定' },
            ]]} onConfirm={(val) => update('bloodPressure', val[0])}>
            {(items, { open }) => (
              <div onClick={open} className='border p-3 rounded cursor-pointer bg-white'>
                血压：{items.length > 0 ? items.map(i => i?.label).join('') : '请选择'}
              </div>
            )}
          </Picker>

          <Picker
            columns={[[
              { label: '正常', value: '正常' },
              { label: '偏高', value: '偏高' },
              { label: '偏低', value: '偏低' },
              { label: '不确定', value: '不确定' },
            ]]} onConfirm={(val) => update('bloodSugar', val[0])}>
            {(items, { open }) => (
              <div onClick={open} className='border p-3 rounded cursor-pointer bg-white'>
                血糖：{items.length > 0 ? items.map(i => i?.label).join('') : '请选择'}
              </div>
            )}
          </Picker>

          <TextArea
            placeholder='请描述您患有的慢性病'
            value={formData.chronic}
            onChange={(val) => update('chronic', val)}
            rows={3}
            className='border p-3 rounded cursor-pointer bg-white'
          />
          <TextArea
            placeholder='当前服用的药物'
            value={formData.medication}
            onChange={(val) => update('medication', val)}
            rows={3}
            className='border p-3 rounded cursor-pointer bg-white'
          />
          <TextArea
            placeholder='饮食忌口（如不能吃糖、海鲜等）'
            value={formData.avoid}
            onChange={(val) => update('avoid', val)}
            rows={3}
            className='border p-3 rounded cursor-pointer bg-white'
          />

          <Button color='primary' size='large' block onClick={handleSubmit}>
            提交信息
          </Button>
        </div>
      </Tabs.Tab>
    </Tabs>
  );
}