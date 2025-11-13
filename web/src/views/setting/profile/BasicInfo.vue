<template>
  <div class="profile-wrapper">
    <!-- 用户信息卡片 -->
    <a-card title="个人信息" class="general-card">
      <template #extra>
        <a-button type="text" @click="onUpdateInfo">
          <template #icon><icon-edit /></template>
          编辑信息
        </a-button>
      </template>
      
      <div class="user-info-body">
        <!-- 头像区域 -->
        <section class="avatar-section">
          <a-upload
            :file-list="avatarList"
            accept="image/*"
            :show-file-list="false"
            list-type="picture-card"
            :show-upload-button="true"
            :on-before-upload="onBeforeUpload"
          >
            <template #upload-button>
              <Avatar :src="avatarList[0].url" :name="userStore.nickname" :size="100" trigger>
                <template #trigger-icon><icon-camera /></template>
              </Avatar>
            </template>
          </a-upload>
          <div class="user-name">
            <span class="nickname">{{ userInfo.nickname }}</span>
            <icon-man v-if="userInfo.gender === 1" style="color: #19bbf1; margin-left: 8px" />
            <icon-woman v-else-if="userInfo.gender === 2" style="color: #fa7fa9; margin-left: 8px" />
          </div>
          <div class="user-id">
            <GiSvgIcon name="id" :size="16" />
            <span>{{ userInfo.id }}</span>
          </div>
        </section>

        <!-- 信息详情 -->
        <a-divider style="margin: 20px 0" />
        <section class="info-section">
          <a-descriptions 
            :column="{ xs: 1, sm: 1, md: 2, lg: 2, xl: 2 }" 
            bordered 
            size="large"
            :label-style="{ width: '120px', fontWeight: '500' }"
          >
            <a-descriptions-item label="用户名">
              <a-space>
                <icon-user />
                <span>{{ userInfo.username }}</span>
              </a-space>
            </a-descriptions-item>
            <a-descriptions-item label="手机号">
              <a-space>
                <icon-phone />
                <span>{{ userInfo.phone || '暂未绑定' }}</span>
              </a-space>
            </a-descriptions-item>
            <a-descriptions-item label="邮箱">
              <a-space>
                <icon-email />
                <span>{{ userInfo.email || '暂未绑定' }}</span>
              </a-space>
            </a-descriptions-item>
            <a-descriptions-item label="部门">
              <a-space>
                <icon-mind-mapping />
                <span>{{ userInfo.deptName }}</span>
              </a-space>
            </a-descriptions-item>
            <a-descriptions-item label="角色" :span="2">
              <a-space>
                <icon-user-group />
                <a-space wrap>
                  <a-tag v-for="(role, index) in userInfo.roles" :key="index" color="arcoblue">
                    {{ role }}
                  </a-tag>
                </a-space>
              </a-space>
            </a-descriptions-item>
            <a-descriptions-item label="注册时间" :span="2">
              <a-space>
                <icon-calendar />
                <span>{{ userInfo.registrationDate }}</span>
              </a-space>
            </a-descriptions-item>
          </a-descriptions>
        </section>
      </div>
    </a-card>

    <!-- 修改密码卡片 -->
    <a-card title="密码管理" class="general-card password-card">
      <div class="password-section">
        <div class="password-info">
          <div class="password-item">
            <GiSvgIcon name="password-color" :size="32" />
            <div class="password-detail">
              <div class="password-title">登录密码</div>
              <div class="password-desc">
                {{ userInfo.pwdResetTime ? '为了您的账号安全，建议定期修改密码' : '请设置密码，可通过账号+密码登录' }}
              </div>
              <div v-if="userInfo.pwdResetTime" class="password-time">
                <icon-clock-circle style="margin-right: 4px" />
                上次修改时间：{{ userInfo.pwdResetTime }}
              </div>
            </div>
          </div>
        </div>
        <a-button type="primary" @click="onUpdatePassword">
          <template #icon><icon-edit /></template>
          修改密码
        </a-button>
      </div>
    </a-card>
  </div>

  <!-- 头像裁剪弹窗 -->
  <a-modal v-model:visible="cropVisible" title="上传头像" :width="width >= 400 ? 400 : '100%'" :footer="false" draggable @close="resetCrop">
    <a-row>
      <a-col :span="14" style="width: 200px; height: 200px">
        <VueCropper
          ref="cropperRef"
          :img="cropOptions.img"
          :info="true"
          :auto-crop="cropOptions.autoCrop"
          :auto-crop-width="cropOptions.autoCropWidth"
          :auto-crop-height="cropOptions.autoCropHeight"
          :fixed-box="cropOptions.fixedBox"
          :fixed="cropOptions.fixed"
          :full="cropOptions.full"
          :center-box="cropOptions.centerBox"
          :can-move="cropOptions.canMove"
          :output-type="cropOptions.outputType"
          :output-size="cropOptions.outputSize"
          @real-time="handleRealTime"
        />
      </a-col>
      <a-col :span="10" style="display: flex; justify-content: center">
        <div :style="previewStyle">
          <div :style="previews.div">
            <img :src="previews.url" :style="previews.img" alt="" />
          </div>
        </div>
      </a-col>
    </a-row>
    <div style="text-align: center; padding-top: 30px">
      <a-space>
        <a-button type="primary" @click="handleUpload">确定</a-button>
        <a-button @click="resetCrop">取消</a-button>
      </a-space>
    </div>
  </a-modal>

  <!-- 修改基本信息弹窗 -->
  <BasicInfoUpdateModal ref="BasicInfoUpdateModalRef" />

  <!-- 修改密码弹窗 -->
  <UpdatePasswordModal ref="UpdatePasswordModalRef" />
</template>

<script setup lang="ts">
import { useWindowSize } from '@vueuse/core'
import { type FileItem, Message } from '@arco-design/web-vue'
import { VueCropper } from 'vue-cropper'
import BasicInfoUpdateModal from './BasicInfoUpdateModal.vue'
import UpdatePasswordModal from './UpdatePasswordModal.vue'
import { uploadAvatar } from '@/apis/system'
import 'vue-cropper/dist/index.css'
import { useUserStore } from '@/stores'
import getAvatar from '@/utils/avatar'

const { width } = useWindowSize()
const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo)

// 头像相关
const avatar = {
  uid: '-2',
  name: 'avatar.png',
  url: userInfo.value.avatar,
}
const avatarList = ref<FileItem[]>([avatar])
const fileRef = ref(reactive({ name: 'avatar.png' }))
const cropOptions: any = reactive({
  img: '',
  autoCrop: true,
  autoCropWidth: 160,
  autoCropHeight: 160,
  fixedBox: true,
  fixed: true,
  full: false,
  centerBox: true,
  canMove: true,
  outputSize: 1,
  outputType: 'png',
})
const cropVisible = ref(false)

// 打开裁剪框
const onBeforeUpload = (file: File): boolean => {
  fileRef.value = file
  const reader = new FileReader()
  reader.readAsDataURL(file)
  reader.onload = () => {
    cropOptions.img = reader.result
  }
  cropVisible.value = true
  return false
}

// 重置裁剪
const resetCrop = () => {
  fileRef.value = { name: '' }
  cropOptions.img = ''
  cropVisible.value = false
}

const previews: any = ref({})
const previewStyle: any = ref({})
// 实时预览
const handleRealTime = (data: any) => {
  previewStyle.value = {
    width: `${data.w}px`,
    height: `${data.h}px`,
    overflow: 'hidden',
    margin: '0',
    zoom: 100 / data.h,
    borderRadius: '50%',
  }
  previews.value = data
}

const cropperRef = ref()
// 上传头像
const handleUpload = async () => {
  cropperRef.value.getCropBlob((data: any) => {
    const formData = new FormData()
    formData.append('avatarFile', data, fileRef.value?.name)
    uploadAvatar(formData).then((res) => {
      userInfo.value.avatar = res.data.avatar
      avatarList.value[0].url = getAvatar(res.data.avatar, undefined)
      resetCrop()
      Message.success('头像更新成功')
    })
  })
}

// 修改基本信息
const BasicInfoUpdateModalRef = ref<InstanceType<typeof BasicInfoUpdateModal>>()
const onUpdateInfo = () => {
  BasicInfoUpdateModalRef.value?.onUpdate()
}

// 修改密码
const UpdatePasswordModalRef = ref<InstanceType<typeof UpdatePasswordModal>>()
const onUpdatePassword = () => {
  UpdatePasswordModalRef.value?.open()
}
</script>

<style scoped lang="scss">
.profile-wrapper {
  max-width: 1000px;
  margin: 0 auto;

  .password-card {
    margin-top: 16px;
  }
}

:deep(.arco-avatar-trigger-icon-button) {
  width: 32px;
  height: 32px;
  line-height: 32px;
  background-color: #e8f3ff;
  .arco-icon-camera {
    margin-top: 8px;
    color: rgb(var(--arcoblue-6));
    font-size: 14px;
  }
}

.user-info-body {
  .avatar-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px 0 24px;

    .user-name {
      margin-top: 16px;
      display: flex;
      align-items: center;
      
      .nickname {
        font-size: 18px;
        font-weight: 500;
        color: var(--color-text-1);
      }
    }

    .user-id {
      margin-top: 8px;
      display: flex;
      align-items: center;
      color: var(--color-text-3);
      font-size: 12px;
      
      span {
        margin-left: 4px;
      }
    }
  }

  .info-section {
    :deep(.arco-descriptions-item-label) {
      color: var(--color-text-2);
    }

    :deep(.arco-descriptions-item-value) {
      color: var(--color-text-1);
    }
  }
}

.password-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;

  .password-info {
    flex: 1;

    .password-item {
      display: flex;
      gap: 16px;
      align-items: flex-start;

      .password-detail {
        flex: 1;

        .password-title {
          font-size: 15px;
          font-weight: 500;
          margin-bottom: 8px;
          color: var(--color-text-1);
        }

        .password-desc {
          color: var(--color-text-2);
          font-size: 13px;
          margin-bottom: 6px;
          line-height: 1.5;
        }

        .password-time {
          color: var(--color-text-3);
          font-size: 12px;
          display: flex;
          align-items: center;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .profile-wrapper {
    max-width: 100%;
  }

  .password-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>

