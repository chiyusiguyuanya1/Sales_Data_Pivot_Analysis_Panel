<script setup>
import { reactive, watch } from "vue";
import {
  COLUMN_DIMENSION_OPTIONS,
  METRIC_OPTIONS,
  ROW_DIMENSION_OPTIONS,
} from "../constants";

const props = defineProps({
  initialConfig: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["change"]);

const form = reactive({
  rowDimension: props.initialConfig.rowDimension,
  columnDimension: props.initialConfig.columnDimension,
  metric: props.initialConfig.metric,
});

watch(
  () => props.initialConfig,
  (value) => {
    form.rowDimension = value.rowDimension;
    form.columnDimension = value.columnDimension;
    form.metric = value.metric;
  },
  { deep: true }
);

watch(
  form,
  (value) => {
    emit("change", { ...value });
  },
  { deep: true }
);
</script>

<template>
  <el-card shadow="never" class="panel-card">
    <template #header>
      <div class="panel-header">
        <div>
          <div class="panel-kicker">透视配置</div>
          <div class="panel-title">动态透视表</div>
        </div>
      </div>
    </template>

    <el-row :gutter="16">
      <el-col :xs="24" :md="8">
        <el-form-item label="行维度">
          <el-select v-model="form.rowDimension" data-testid="row-dimension">
            <el-option
              v-for="item in ROW_DIMENSION_OPTIONS"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :xs="24" :md="8">
        <el-form-item label="列维度">
          <el-select v-model="form.columnDimension" data-testid="column-dimension">
            <el-option
              v-for="item in COLUMN_DIMENSION_OPTIONS"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :xs="24" :md="8">
        <el-form-item label="指标">
          <el-select v-model="form.metric" data-testid="metric-select">
            <el-option
              v-for="item in METRIC_OPTIONS"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>
  </el-card>
</template>
