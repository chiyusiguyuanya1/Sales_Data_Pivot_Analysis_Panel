<script setup>
import { reactive, watch } from "vue";

const props = defineProps({
  meta: {
    type: Object,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  initialFilters: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["search", "reset", "open-create"]);

const form = reactive({
  startDate: props.initialFilters.startDate,
  endDate: props.initialFilters.endDate,
  cities: [...props.initialFilters.cities],
  categories: [...props.initialFilters.categories],
  salespeople: [...props.initialFilters.salespeople],
  paymentStatus: props.initialFilters.paymentStatus,
  minAmount: props.initialFilters.minAmount,
  maxAmount: props.initialFilters.maxAmount,
});

watch(
  () => props.initialFilters,
  (value) => {
    form.startDate = value.startDate;
    form.endDate = value.endDate;
    form.cities = [...value.cities];
    form.categories = [...value.categories];
    form.salespeople = [...value.salespeople];
    form.paymentStatus = value.paymentStatus;
    form.minAmount = value.minAmount;
    form.maxAmount = value.maxAmount;
  },
  { deep: true }
);

function submit() {
  emit("search", {
    startDate: form.startDate || "",
    endDate: form.endDate || "",
    cities: [...form.cities],
    categories: [...form.categories],
    salespeople: [...form.salespeople],
    paymentStatus: form.paymentStatus || "",
    minAmount: form.minAmount ?? "",
    maxAmount: form.maxAmount ?? "",
  });
}

function reset() {
  form.startDate = "";
  form.endDate = "";
  form.cities = [];
  form.categories = [];
  form.salespeople = [];
  form.paymentStatus = "";
  form.minAmount = null;
  form.maxAmount = null;
  emit("reset");
}
</script>

<template>
  <el-card shadow="never" class="panel-card">
    <template #header>
      <div class="panel-header">
        <div>
          <div class="panel-kicker">筛选区</div>
          <div class="panel-title">订单查询条件</div>
        </div>
        <div class="panel-actions">
          <el-button class="ghost-button" @click="emit('open-create')" type="success" plain>
            新增订单
          </el-button>
          <el-button class="ghost-button" @click="reset" :disabled="loading">
            重置条件
          </el-button>
        </div>
      </div>
    </template>

    <el-form label-position="top" @submit.prevent="submit">
      <el-row :gutter="18">
        <el-col :xs="24" :md="12" :xl="6">
          <el-form-item label="开始日期">
            <el-date-picker
              v-model="form.startDate"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="选择开始日期"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12" :xl="6">
          <el-form-item label="结束日期">
            <el-date-picker
              v-model="form.endDate"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="选择结束日期"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12" :xl="6">
          <el-form-item label="商品类别">
            <el-select
              v-model="form.categories"
              multiple
              filterable
              collapse-tags
              collapse-tags-tooltip
              placeholder="全部类别"
            >
              <el-option
                v-for="item in meta.categories"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12" :xl="6">
          <el-form-item label="支付状态">
            <el-radio-group v-model="form.paymentStatus" class="payment-status-group">
              <el-radio-button label="">全部订单</el-radio-button>
              <el-radio-button label="paid">已支付</el-radio-button>
              <el-radio-button label="unpaid">未支付</el-radio-button>
            </el-radio-group>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12" :xl="8">
          <el-form-item label="城市多选">
            <el-select
              v-model="form.cities"
              multiple
              filterable
              collapse-tags
              collapse-tags-tooltip
              placeholder="全部城市"
              data-testid="city-filter"
            >
              <el-option v-for="item in meta.cities" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12" :xl="8">
          <el-form-item label="销售员">
            <el-select
              v-model="form.salespeople"
              multiple
              filterable
              collapse-tags
              collapse-tags-tooltip
              placeholder="全部销售员"
            >
              <el-option
                v-for="item in meta.salespeople"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12" :xl="4">
          <el-form-item label="最低金额">
            <el-input-number
              v-model="form.minAmount"
              :min="0"
              :precision="2"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12" :xl="4">
          <el-form-item label="最高金额">
            <el-input-number
              v-model="form.maxAmount"
              :min="0"
              :precision="2"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <div class="form-footer">
        <el-button
          type="primary"
          class="primary-button"
          :loading="loading"
          data-testid="search-button"
          @click="submit"
        >
          查询数据
        </el-button>
      </div>
    </el-form>
  </el-card>
</template>
