export const ROW_DIMENSION_OPTIONS = [
  { label: "城市", value: "city" },
  { label: "商品类别", value: "category" },
  { label: "销售员", value: "salesperson" },
];

export const COLUMN_DIMENSION_OPTIONS = [
  { label: "月份", value: "month" },
  { label: "支付状态", value: "paymentStatus" },
];

export const METRIC_OPTIONS = [
  { label: "订单数", value: "orderCount" },
  { label: "销售额", value: "amount" },
  { label: "净销售额", value: "netAmount" },
  { label: "平均客单价", value: "avgAmount" },
];

export const EMPTY_SUMMARY = [
  { label: "总订单数", value: "0", hint: "当前筛选结果为空" },
  { label: "总销售额", value: "0.00", hint: "amount 汇总值" },
  { label: "支付率", value: "0.0%", hint: "已支付订单数 / 总订单数" },
  { label: "销售额最高城市", value: "-", hint: "无可统计城市" },
];
