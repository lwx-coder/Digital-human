<template>
  <div class="errPage-container">
    <el-row>
      <el-col :span="12">
        <h1 class="text-jumbo text-ginormous">401</h1>
        <h2>您没有权限访问该页面</h2>
        <h6>抱歉，您没有权限访问此页面</h6>
        <ul class="list-unstyled">
          <li class="link-type">
            <router-link to="/">
              回到首页
            </router-link>
          </li>
        </ul>
      </el-col>
      <el-col :span="12">
        <img src="#" width="313" height="428" alt="无权限访问图片">
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'Page401',
  data() {
    return {}
  }
}
</script>

<style lang="scss" scoped>
.errPage-container {
  width: 800px;
  max-width: 100%;
  margin: 100px auto;
  .text-jumbo {
    font-size: 60px;
    font-weight: 700;
    color: #484848;
  }
  .text-ginormous {
    font-size: 100px;
    color: #f44336;
  }
  h2 {
    font-size: 24px;
    color: #484848;
  }
  h6 {
    font-size: 16px;
    color: #777;
  }
  .list-unstyled {
    font-size: 16px;
    li {
      padding-bottom: 10px;
    }
    a {
      color: #3296fa;
      text-decoration: none;
      &:hover {
        text-decoration: underline;
      }
    }
  }
}
</style>
