<script setup>
import { computed } from "vue";
import { formatMetric } from "../utils/formatters";

const props = defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: "",
  },
  pivot: {
    type: Object,
    default: null,
  },
  metric: {
    type: String,
    required: true,
  },
});

const tableRows = computed(() => {
  if (!props.pivot) {
    return [];
  }

  return props.pivot.rows.map((row) => ({
    rowKey: row.rowKey,
    cells: row.cells,
    total: row.total,
  }));
});
</script>

<template>
  <el-card shadow="never" class="panel-card">
    <template #header>
      <div class="panel-header">
        <div>
          <div class="panel-kicker">透视结果</div>
          <div class="panel-title">多维销售数据矩阵</div>
        </div>
      </div>
    </template>

    <el-alert
      v-if="pivot"
      type="info"
      show-icon
      :closable="false"
      class="table-note"
      :title="pivot.metricDescription"
    />

    <el-alert
      v-if="error"
      type="error"
      show-icon
      :closable="false"
      class="table-note"
      :title="error"
    />

    <el-skeleton v-if="loading" :rows="6" animated />

    <el-empty
      v-else-if="!pivot || !pivot.rows.length"
      description="当前筛选条件下没有订单数据"
    />

    <div v-else class="pivot-scroll-shell" data-testid="pivot-table">
      <table class="pivot-grid">
        <thead>
          <tr>
            <th class="sticky-left">{{ pivot.rowLabel }} / {{ pivot.columnLabel }}</th>
            <th v-for="column in pivot.columns" :key="column">{{ column }}</th>
            <th>合计</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in tableRows" :key="row.rowKey">
            <th class="sticky-left row-header">{{ row.rowKey }}</th>
            <td v-for="cell in row.cells" :key="cell.key">
              {{ formatMetric(metric, cell.rawValue) }}
            </td>
            <td class="total-cell">{{ formatMetric(metric, row.total) }}</td>
          </tr>
          <tr class="grand-total-row">
            <th class="sticky-left row-header">合计</th>
            <td v-for="column in pivot.columnTotals" :key="column.key">
              {{ formatMetric(metric, column.total) }}
            </td>
            <td class="total-cell">{{ formatMetric(metric, pivot.grandTotal) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </el-card>
</template>
