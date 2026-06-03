import { EMPTY_SUMMARY } from "../constants";
import { formatCurrency, formatPercent } from "./formatters";

const COLUMN_LABELS = {
  month: "月份",
  paymentStatus: "支付状态",
};

const ROW_LABELS = {
  city: "城市",
  category: "商品类别",
  salesperson: "销售员",
};

function getMonthLabel(createdAt) {
  return createdAt.slice(0, 7);
}

function getPaymentLabel(order) {
  return order.is_paid === 1 ? "已支付" : "未支付";
}

function getColumnValue(order, columnDimension) {
  return columnDimension === "month" ? getMonthLabel(order.created_at) : getPaymentLabel(order);
}

function createMetricAccumulator() {
  return {
    orderCount: 0,
    amount: 0,
    netAmount: 0,
  };
}

function consumeOrder(accumulator, order) {
  accumulator.orderCount += 1;
  accumulator.amount += Number(order.amount);
  accumulator.netAmount += Number(order.amount) - Number(order.refund_amount);
}

function readMetric(metric, accumulator) {
  if (!accumulator) {
    return 0;
  }

  if (metric === "orderCount") {
    return accumulator.orderCount;
  }

  if (metric === "amount") {
    return accumulator.amount;
  }

  if (metric === "netAmount") {
    return accumulator.netAmount;
  }

  if (metric === "avgAmount") {
    return accumulator.orderCount ? accumulator.amount / accumulator.orderCount : 0;
  }

  return 0;
}

function collectColumns(orders, columnDimension) {
  if (!orders.length) {
    return [];
  }

  if (columnDimension === "paymentStatus") {
    return ["已支付", "未支付"];
  }

  const months = Array.from(new Set(orders.map((order) => getMonthLabel(order.created_at)))).sort();
  const result = [];
  let current = new Date(`${months[0]}-01T00:00:00`);
  const end = new Date(`${months[months.length - 1]}-01T00:00:00`);

  while (current <= end) {
    const year = current.getFullYear();
    const month = String(current.getMonth() + 1).padStart(2, "0");
    result.push(`${year}-${month}`);
    current.setMonth(current.getMonth() + 1);
  }

  return result;
}

export function buildSummary(orders) {
  if (!orders.length) {
    return EMPTY_SUMMARY;
  }

  const totalAmount = orders.reduce((sum, order) => sum + Number(order.amount), 0);
  const paidCount = orders.filter((order) => order.is_paid === 1).length;
  const cityTotals = orders.reduce((acc, order) => {
    acc[order.city] = (acc[order.city] || 0) + Number(order.amount);
    return acc;
  }, {});
  const topCity = Object.entries(cityTotals).sort((a, b) => b[1] - a[1])[0];

  return [
    { label: "总订单数", value: String(orders.length), hint: "当前筛选结果订单条数" },
    { label: "总销售额", value: formatCurrency(totalAmount), hint: "amount 求和" },
    { label: "支付率", value: formatPercent(paidCount / orders.length), hint: "已支付订单数 / 总订单数" },
    {
      label: "销售额最高城市",
      value: topCity ? topCity[0] : "-",
      hint: topCity ? `销售额 ${formatCurrency(topCity[1])}` : "无可统计城市",
    },
  ];
}

export function buildPivotView(orders, rowDimension, columnDimension, metric) {
  const rows = Array.from(new Set(orders.map((order) => order[rowDimension]))).sort((a, b) =>
    String(a).localeCompare(String(b), "zh-CN")
  );
  const columns = collectColumns(orders, columnDimension);
  const rowBuckets = {};
  const columnBuckets = {};
  const matrixBuckets = {};
  const grandBucket = createMetricAccumulator();

  rows.forEach((rowKey) => {
    rowBuckets[rowKey] = createMetricAccumulator();
    matrixBuckets[rowKey] = {};

    columns.forEach((columnKey) => {
      matrixBuckets[rowKey][columnKey] = createMetricAccumulator();
    });
  });

  columns.forEach((columnKey) => {
    columnBuckets[columnKey] = createMetricAccumulator();
  });

  orders.forEach((order) => {
    const rowKey = order[rowDimension];
    const columnKey = getColumnValue(order, columnDimension);

    consumeOrder(rowBuckets[rowKey], order);
    consumeOrder(columnBuckets[columnKey], order);
    consumeOrder(matrixBuckets[rowKey][columnKey], order);
    consumeOrder(grandBucket, order);
  });

  const tableRows = rows.map((rowKey) => {
    const cells = columns.map((columnKey) => ({
      key: columnKey,
      rawValue: readMetric(metric, matrixBuckets[rowKey][columnKey]),
    }));

    return {
      rowKey,
      cells,
      total: readMetric(metric, rowBuckets[rowKey]),
    };
  });

  const columnTotals = columns.map((columnKey) => ({
    key: columnKey,
    total: readMetric(metric, columnBuckets[columnKey]),
  }));

  return {
    rowLabel: ROW_LABELS[rowDimension],
    columnLabel: COLUMN_LABELS[columnDimension],
    columns,
    rows: tableRows,
    columnTotals,
    grandTotal: readMetric(metric, grandBucket),
    metricDescription:
      metric === "avgAmount"
        ? "平均客单价 = 当前分组内 amount 总和 / 当前分组订单数，合计按整体口径重新计算。"
        : "摘要卡片和透视表均基于当前筛选后的同一批原始订单数据计算。",
  };
}
