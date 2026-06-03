<script setup>
defineProps({
  items: {
    type: Array,
    required: true,
  },
});
</script>

<template>
  <el-row :gutter="18" class="summary-row">
    <el-col v-for="item in items" :key="item.label" :xs="24" :sm="12" :lg="6">
      <el-card shadow="hover" class="summary-card">
        <div class="summary-label">{{ item.label }}</div>
        <div class="summary-value">{{ item.value }}</div>
        <div class="summary-hint">{{ item.hint }}</div>
      </el-card>
    </el-col>
  </el-row>
</template>
