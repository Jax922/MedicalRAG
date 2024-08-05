"use client";

import React, { Component } from 'react';
import dynamic from 'next/dynamic';

const ReactEcharts = dynamic(() => import('echarts-for-react'), { ssr: false });

interface EChartsComponentProps {
  option: any;
}

class EChartsComponent extends Component<EChartsComponentProps> {
  componentDidMount() {
    // 动态导入 echarts 及其插件
    import('echarts').then(echarts => {
      import('echarts-wordcloud');
    });
  }

  render() {
    return <ReactEcharts option={this.props.option} style={{ height: '400px', width: '100%' }} />;
  }
}

export default EChartsComponent;
