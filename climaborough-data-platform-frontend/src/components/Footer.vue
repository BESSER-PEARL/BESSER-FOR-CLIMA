<script setup>

</script>

<template>
  <div class="footer">
    <!-- First level content (20% height) -->
    <div class="image-wrapper">
      <div class="first-level">
        <div class="column"> <img src="/climaborough-logo-white-300x84.png" alt="Your Image" class="footer-image"></div>
        <div class="column">
          <img src="/EN_Co-fundedbytheEU_RGB_POS.png" alt="Alt" style="width: 300px;">
        </div>

      </div>

    </div>


    <!-- Second level content (80% height) -->
    <div class="second-level">
      <div class="column">

        <p v-html="$t('footer.column1')"></p>
      </div>
      <div class="column">
        <p>{{ $t('footer.column2') }}</p>
      </div>
    </div>
    <div class="third-level">
      <span style="font-weight: bold; color: white; font-size: large;">{{ $t('footer.tos') }}</span>
      <span class="separator"></span>
      <span style="font-weight: bold; color: white; font-size: large;">{{ $t('footer.socialMedia') }}</span>
      <span style="margin-left: 10px;">
        <a href="https://www.linkedin.com/company/climaborough/" target="_blank">
          <Icon icon="fa-brands:linkedin" width="30" height="30" style="color: white" />
        </a>
        <a href="https://www.facebook.com/climaborough" target="_blank">
          <Icon icon="fa6-brands:facebook-f" width="30" height="30"
            href="https://www.linkedin.com/company/climaborough/" style="color: white" />
        </a>
        <a href="https://www.instagram.com/climaborough/" target="_blank">
          <Icon icon="fa-brands:instagram" width="30" height="30" style="color: white" />
        </a>
        <a href="https://twitter.com/Climaborough" target="_blank">
          <Icon icon="fa6-brands:x-twitter" width="30" height="30" style="color: white" />
        </a>
        <a href="https://www.youtube.com/@Climaborough" target="_blank">
          <Icon icon="fa6-brands:youtube" width="30" height="30" style="color: white" />
        </a>

      </span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.separator {
  border-left: 2px solid #ffffff;
  /* Adjust the color and thickness */
  height: 30px;
  /* Adjust the height as needed */
  margin: 0 10px;
  /* Adjust the spacing */

}

.first-level {
  height: 10%;
  display: flex;
  padding-top: 20px;
  margin: 20px 100px 10px 60px
}

.image-wrapper {
  padding: 5px;
  /* Adjust the padding as needed */
}

.footer-image {
  width: 230px;
}

.second-level {
  height: 85%;
  display: flex;
  padding-bottom: 15px;
  margin: 0px 100px 10px 60px
}

.third-level {
  height: 5%;
  display: flex;
  border-top: 4px solid rgba(255, 255, 255, 0.3);
  padding-top: 10px;
  text-align: right;
  justify-content: right;
  padding: 10px;
  align-items: center;
}

.column {
  flex: 1;
  padding-left: 60px;
  padding-right: 60px;
}

a {
  padding: 7px;
}
</style>
