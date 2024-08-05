// app/echarts/page.tsx

"use client";

import React, { Component } from 'react';
import dynamic from 'next/dynamic';
import * as echarts from 'echarts';

const EChartsComponent = dynamic(() => import('../../components/EChartsComponent'), { ssr: false });

class MyPage extends Component {
    chatRecords = [
        { "role": "user", "content": "我头痛已经三天了。" },
        { "role": "assistant", "content": "您是否有其他症状？" },
        { "role": "user", "content": "我还有点发烧。" },
        { "role": "assistant", "content": "请多喝水，休息一下。" },
        { "role": "user", "content": "最近咳嗽得厉害，晚上睡不好。" },
        { "role": "assistant", "content": "那真的很辛苦。咳嗽多久了？" },
        { "role": "user", "content": "大概有一周了。" },
        { "role": "assistant", "content": "除了咳嗽，还有其他症状吗，比如胸痛或者呼吸困难？" },
        { "role": "user", "content": "有时候会觉得胸闷。" },
        { "role": "assistant", "content": "明白了，胸闷可能是因为咳嗽引起的。你有没有尝试过一些止咳药？" },
        { "role": "user", "content": "还没有。" },
        { "role": "assistant", "content": "我建议你尝试一些温和的止咳药，当然，多喝温水也有帮助。如果情况没有好转，最好去看医生。" }
    ]

  symptomFrequency = this.chatRecords.reduce<{ [key: string]: number }>((acc, record) => {
    if (record.role === 'user') {
      const words = record.content.split(/[\s，。]+/);
      words.forEach(word => {
        if (!acc[word]) {
          acc[word] = 0;
        }
        acc[word]++;
      });
    }
    return acc;
  }, {});

  symptomData = Object.keys(this.symptomFrequency).map(symptom => ({
    name: symptom,
    value: this.symptomFrequency[symptom]
  }));

  timelineData = this.chatRecords.map((record, index) => ({
    name: `记录 ${index + 1}`,
    value: index
  }));

  scatterData = this.chatRecords.map((record, index) => [index, record.role === 'user' ? 1 : 0]);

  wordCloudOption: echarts.EChartsOption = {
    series: [{
      type: 'wordCloud',
      data: this.symptomData,
      shape: 'circle', // 可以根据需求调整
      width: '100%',
      height: '100%',
    }]
  };

  barChartOption: echarts.EChartsOption = {
    xAxis: {
      type: 'category',
      data: Object.keys(this.symptomFrequency)
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: Object.values(this.symptomFrequency),
      type: 'bar'
    }]
  };

  timelineChartOption: echarts.EChartsOption = {
    baseOption: {
      timeline: {
        data: this.chatRecords.map((_, index) => `记录 ${index + 1}`),
        axisType: 'category',
      },
      xAxis: {
        type: 'category',
      },
      yAxis: {
        type: 'value',
      },
      series: [{
        type: 'line',
        data: this.chatRecords.map((record, index) => ({ name: `记录 ${index + 1}`, value: index }))
      }]
    },
    options: this.chatRecords.map((_, index) => ({
      series: [{
        data: [index]
      }]
    }))
  };

  pieChartOption: echarts.EChartsOption = {
    series: [{
      type: 'pie',
      data: this.symptomData
    }]
  };

  scatterPlotOption: echarts.EChartsOption = {
    xAxis: {
      type: 'category',
      data: this.chatRecords.map((record, index) => `记录 ${index + 1}`)
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      type: 'scatter',
      data: this.scatterData
    }]
  };

  histogramOption: echarts.EChartsOption = {
    xAxis: {
      type: 'category',
      data: Object.keys(this.symptomFrequency)
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: Object.values(this.symptomFrequency),
      type: 'bar'
    }]
  };

  async componentDidMount() {
    // 确保 `echarts` 和 `echarts-wordcloud` 插件正确加载
    await import('echarts-wordcloud');
  }

  render() {
    return (
      <div>
        <h2>词云图</h2>
        <EChartsComponent option={this.wordCloudOption} />

        <h2>条形图</h2>
        <EChartsComponent option={this.barChartOption} />

        <h2>时间轴图</h2>
        <EChartsComponent option={this.timelineChartOption} />

        <h2>饼图</h2>
        <EChartsComponent option={this.pieChartOption} />

        <h2>散点图</h2>
        <EChartsComponent option={this.scatterPlotOption} />

        <h2>词频统计图</h2>
        <EChartsComponent option={this.histogramOption} />
      </div>
    );
  }
}

export default MyPage;
