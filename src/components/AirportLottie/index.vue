<template>
  <div 
    class="lottie-container" 
    ref="container" 
    :style="{ width: width, height: height }"
  ></div>
</template>

<script>
import lottie from 'lottie-web'

export default {
  name: 'AirportLottie',
  props: {
    animationPath: {
      type: String,
      required: true
    },
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '100%'
    },
    loop: {
      type: Boolean,
      default: true
    },
    autoplay: {
      type: Boolean,
      default: true
    },
    speed: {
      type: Number,
      default: 1
    }
  },
  data() {
    return {
      animation: null
    }
  },
  mounted() {
    this.loadAnimation()
  },
  beforeDestroy() {
    if (this.animation) {
      this.animation.destroy()
    }
  },
  methods: {
    loadAnimation() {
      if (this.animation) {
        this.animation.destroy()
      }

      this.animation = lottie.loadAnimation({
        container: this.$refs.container,
        renderer: 'svg',
        loop: this.loop,
        autoplay: this.autoplay,
        path: this.animationPath,
        rendererSettings: {
          preserveAspectRatio: 'xMidYMid slice'
        }
      })

      this.animation.setSpeed(this.speed)

      this.animation.addEventListener('DOMLoaded', () => {
        this.$emit('animation-loaded')
      })

      this.animation.addEventListener('complete', () => {
        this.$emit('animation-complete')
      })
    },
    play() {
      if (this.animation) {
        this.animation.play()
      }
    },
    pause() {
      if (this.animation) {
        this.animation.pause()
      }
    },
    stop() {
      if (this.animation) {
        this.animation.stop()
      }
    }
  },
  watch: {
    animationPath() {
      this.loadAnimation()
    },
    speed(newSpeed) {
      if (this.animation) {
        this.animation.setSpeed(newSpeed)
      }
    }
  }
}
</script>

<style scoped>
.lottie-container {
  overflow: hidden;
}
</style> 