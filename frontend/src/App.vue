<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { createOrder, fetchMeta, fetchOrders } from "./api";
import DashboardHeader from "./components/DashboardHeader.vue";
import SummaryCards from "./components/SummaryCards.vue";
import FilterPanel from "./components/FilterPanel.vue";
import PivotConfig from "./components/PivotConfig.vue";
import PivotTable from "./components/PivotTable.vue";
import CreateOrderDialog from "./components/CreateOrderDialog.vue";
import { EMPTY_SUMMARY } from "./constants";
import { buildPivotView, buildSummary } from "./utils/pivot";

const meta = reactive({
  cities: [],
  categories: [],
  salespeople: [],
});

const filters = reactive({
  startDate: "",
  endDate: "",
  cities: [],
  categories: [],
  salespeople: [],
  paymentStatus: "",
  minAmount: null,
  maxAmount: null,
});

const pivotConfig = reactive({
  rowDimension: "city",
  columnDimension: "month",
  metric: "amount",
});

const orders = ref([]);
const loading = ref(false);
const createLoading = ref(false);
const errorMessage = ref("");
const createDialogVisible = ref(false);

const summaryItems = computed(() =>
  orders.value.length ? buildSummary(orders.value) : EMPTY_SUMMARY
);

const pivotView = computed(() => {
  if (!orders.value.length) {
    return null;
  }

  return buildPivotView(
    orders.value,
    pivotConfig.rowDimension,
    pivotConfig.columnDimension,
    pivotConfig.metric
  );
});

function buildApiFilters() {
  const params = {
    startDate: filters.startDate,
    endDate: filters.endDate,
    cities: filters.cities,
    categories: filters.categories,
    salespeople: filters.salespeople,
    paymentStatus: filters.paymentStatus,
    minAmount: filters.minAmount,
    maxAmount: filters.maxAmount,
  };

  if (filters.paymentStatus === "paid") {
    params.paidOnly = "true";
  }

  return params;
}

async function loadMeta() {
  const payload = await fetchMeta();
  meta.cities = payload.data.cities || [];
  meta.categories = payload.data.categories || [];
  meta.salespeople = payload.data.salespeople || [];
}

async function loadOrders() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const payload = await fetchOrders(buildApiFilters());
    orders.value = payload.data || [];
  } catch (error) {
    orders.value = [];
    errorMessage.value = error.message || "订单查询失败";
  } finally {
    loading.value = false;
  }
}

function handleSearch(nextFilters) {
  Object.assign(filters, nextFilters);
  loadOrders();
}

function handleReset() {
  filters.startDate = "";
  filters.endDate = "";
  filters.cities = [];
  filters.categories = [];
  filters.salespeople = [];
  filters.paymentStatus = "";
  filters.minAmount = null;
  filters.maxAmount = null;
  loadOrders();
}

function handlePivotChange(nextConfig) {
  Object.assign(pivotConfig, nextConfig);
}

async function handleCreateOrder(payload) {
  createLoading.value = true;

  try {
    await createOrder(payload);
    ElMessage.success("订单新增成功");
    createDialogVisible.value = false;
    await loadMeta();
    await loadOrders();
  } catch (error) {
    ElMessage.error(error.message || "新增订单失败");
  } finally {
    createLoading.value = false;
  }
}

onMounted(async () => {
  try {
    await loadMeta();
    await loadOrders();
  } catch (error) {
    errorMessage.value = error.message || "初始化失败";
  }
});
</script>

<template>
  <div class="app-shell">
    <div class="ambient ambient-a"></div>
    <div class="ambient ambient-b"></div>

    <main class="dashboard-layout">
      <DashboardHeader />

      <FilterPanel
        :meta="meta"
        :loading="loading"
        :initial-filters="filters"
        @search="handleSearch"
        @reset="handleReset"
        @open-create="createDialogVisible = true"
      />

      <SummaryCards :items="summaryItems" />

      <PivotConfig :initial-config="pivotConfig" @change="handlePivotChange" />

      <PivotTable
        :loading="loading"
        :error="errorMessage"
        :pivot="pivotView"
        :metric="pivotConfig.metric"
      />
    </main>

    <CreateOrderDialog
      v-model:visible="createDialogVisible"
      :meta="meta"
      :loading="createLoading"
      @submit="handleCreateOrder"
    />
  </div>
</template>
