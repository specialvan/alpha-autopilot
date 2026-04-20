export const overview = {
  matrixVersion: 'v003',
  healthValue: 82,
  sampleCount: 10,
  versionCount: 3,
  hitRate: '76%',
  riskScore: 34,
};

export const narrativeSignals = [
  { label: '主线推进', value: 61 },
  { label: '冲突强度', value: 64 },
  { label: '伏笔负载', value: 36 },
  { label: '回收压力', value: 31 },
];

export const matrixWeights = [
  ['冲突推进', '1.32'],
  ['情绪回报', '1.18'],
  ['钩子强度', '1.09'],
  ['连续性安全', '1.24'],
  ['人物聚焦', '0.96'],
  ['伏笔价值', '1.12'],
  ['节奏适配', '1.04'],
] as const;

export const recommendations = [
  {
    action: '推进主线冲突',
    score: '0.924',
    description: '在合法前提下优先放大对抗压力，推动下一章进入高张力区间。',
    top: true,
  },
  {
    action: '埋设伏笔',
    score: '0.841',
    description: '适合在中段补齐信息缺口，为后续爆发保留解释空间。',
    top: false,
  },
  {
    action: '回收旧钩子',
    score: '0.799',
    description: '在当前回收压力上升时，把前文悬而未决的信息转化为情绪回报。',
    top: false,
  },
];

export const feedbackNotes = [
  '早期开篇样本对冲突推进的权重修正最明显。',
  '中段样本提高了伏笔与节奏的联动强度。',
  '后段样本增强了回收压力与情绪回报的相关性。',
];

export const logs = [
  { time: '2026-04-21 10:41', text: 'v001 初始矩阵生成，完成 10 条样本训练。' },
  { time: '2026-04-21 11:08', text: '补充中段样本，伏笔与节奏权重上调。' },
  { time: '2026-04-21 11:32', text: '增加后段样本，回收压力与情绪回报闭环增强。' },
];
