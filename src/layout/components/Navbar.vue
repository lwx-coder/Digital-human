<template>
  <div class="navbar">
    <hamburger :is-active="sidebar.opened" class="hamburger-container" @toggleClick="toggleSideBar" />

    <breadcrumb class="breadcrumb-container" />

    <div class="right-menu">
      <el-dropdown class="avatar-container" trigger="click">
        <div class="avatar-wrapper">
          <img v-if="avatar" :src="avatar" class="user-avatar">
          <img v-else src="@/assets/avatar.png" class="user-avatar">
          <span class="user-name">{{ name }}</span>
          <i class="el-icon-caret-bottom" />
        </div>
        <el-dropdown-menu slot="dropdown" class="user-dropdown">
          <router-link to="/">
            <el-dropdown-item>
              <i class="el-icon-s-home"></i> 首页
            </el-dropdown-item>
          </router-link>
          <router-link :to="profileLink">
            <el-dropdown-item>
              <i class="el-icon-user"></i> 个人中心
            </el-dropdown-item>
          </router-link>
          <el-dropdown-item divided @click.native="handleLogout">
            <i class="el-icon-switch-button"></i> 退出登录
          </el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import Breadcrumb from '@/components/Breadcrumb'
import Hamburger from '@/components/Hamburger'

export default {
  components: {
    Breadcrumb,
    Hamburger
  },
  computed: {
    ...mapGetters([
      'sidebar',
      'avatar',
      'name',
      'roles'
    ]),
    profileLink() {
      // 根据角色返回不同的个人中心路径
      if (this.roles && this.roles.includes('passenger')) {
        return '/passenger-management/passenger/profile'
      } else {
        // 默认路径或管理员路径
        return '/profile'
      }
    }
  },
  methods: {
    toggleSideBar() {
      this.$store.dispatch('app/toggleSideBar')
    },
    handleLogout() {
      this.$confirm('确认退出系统吗?', '退出提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async() => {
        try {
          await this.$store.dispatch('user/logout')
          this.$message.success('退出登录成功')
          this.$router.push(`/login`)
        } catch (error) {
          console.error('退出登录失败:', error)
          this.$message.error('退出登录失败，请重试')
        }
      }).catch(() => {
        this.$message.info('已取消退出')
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.navbar {
  height: 50px;
  overflow: hidden;
  position: relative;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);

  .hamburger-container {
    line-height: 46px;
    height: 100%;
    float: left;
    cursor: pointer;
    transition: background .3s;
    -webkit-tap-highlight-color:transparent;

    &:hover {
      background: rgba(0, 0, 0, .025)
    }
  }

  .breadcrumb-container {
    float: left;
  }

  .right-menu {
    float: right;
    height: 100%;
    line-height: 50px;

    &:focus {
      outline: none;
    }

    .right-menu-item {
      display: inline-block;
      padding: 0 8px;
      height: 100%;
      font-size: 18px;
      color: #5a5e66;
      vertical-align: text-bottom;

      &.hover-effect {
        cursor: pointer;
        transition: background .3s;

        &:hover {
          background: rgba(0, 0, 0, .025)
        }
      }
    }

    .avatar-container {
      margin-right: 30px;

      .avatar-wrapper {
        margin-top: 5px;
        position: relative;
        display: flex;
        align-items: center;

        .user-avatar {
          cursor: pointer;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          object-fit: contain;
        }
        
        .user-name {
          margin: 0 5px 0 8px;
          color: #606266;
          font-size: 14px;
        }

        .el-icon-caret-bottom {
          cursor: pointer;
          font-size: 12px;
          color: #606266;
        }
      }
    }
  }
}

.user-dropdown {
  .el-dropdown-item {
    display: flex !important;
    align-items: center;
    
    i {
      margin-right: 8px;
      font-size: 16px;
    }
  }
}
</style>
