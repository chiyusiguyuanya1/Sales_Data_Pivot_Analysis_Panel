<script setup>
import { computed, reactive, ref, watch } from "vue";

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  meta: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["update:visible", "submit"]);

const formRef = ref();
const form = reactive({
  order_no: "",
  city: "",
  category: "",
  salesperson: "",
  amount: 0,
  refund_amount: 0,
  is_paid: 1,
  created_at: "",
});

const visibleState = computed({
  get: () => props.visible,
  set: (value) => emit("update:visible", value),
});

const rules = {
  order_no: [{ required: true, message: "请输入订单号", trigger: "blur" }],
  city: [{ required: true, message: "请选择城市", trigger: "change" }],
  category: [{ required: true, message: "请选择商品类别", trigger: "change" }],
  salesperson: [{ required: true, message: "请选择销售员", trigger: "change" }],
  amount: [{ required: true, message: "请输入订单金额", trigger: "change" }],
  created_at: [{ required: true, message: "请选择下单时间", trigger: "change" }],
};

function resetForm() {
  form.order_no = "";
  form.city = props.meta.cities[0] || "";
  form.category = props.meta.categories[0] || "";
  form.salesperson = props.meta.salespeople[0] || "";
  form.amount = 0;
  form.refund_amount = 0;
  form.is_paid = 1;
  form.created_at = "";
}

watch(
  () => props.visible,
  (value) => {
    if (value) {
      resetForm();
    }
  }
);

async function submit() {
  await formRef.value.validate();
  emit("submit", { ...form });
}
</script>

<template>
  <el-dialog v-model="visibleState" title="新增订单" width="640px">
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="订单号" prop="order_no">
            <el-input v-model="form.order_no" data-testid="order-no-input" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="下单时间" prop="created_at">
            <el-date-picker
              v-model="form.created_at"
              type="datetime"
              value-format="YYYY-MM-DD HH:mm:ss"
              placeholder="选择下单时间"
              data-testid="created-at-input"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="城市" prop="city">
            <el-select v-model="form.city" filterable allow-create default-first-option>
              <el-option v-for="item in meta.cities" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="商品类别" prop="category">
            <el-select v-model="form.category" filterable allow-create default-first-option>
              <el-option
                v-for="item in meta.categories"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="销售员" prop="salesperson">
            <el-select v-model="form.salesperson" filterable allow-create default-first-option>
              <el-option
                v-for="item in meta.salespeople"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="支付状态">
            <el-switch
              v-model="form.is_paid"
              :active-value="1"
              :inactive-value="0"
              active-text="已支付"
              inactive-text="未支付"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="订单金额" prop="amount">
            <el-input-number
              v-model="form.amount"
              :min="0"
              :precision="2"
              data-testid="amount-input"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="退款金额">
            <el-input-number
              v-model="form.refund_amount"
              :min="0"
              :precision="2"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="visibleState = false">取消</el-button>
        <el-button type="primary" :loading="loading" data-testid="submit-order" @click="submit">
          提交订单
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>
