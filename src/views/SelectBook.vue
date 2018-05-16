<template>
  <div>
  <my-navbar></my-navbar>
  <div class="container">
    <body>
    <h1 align="left">个人选书</h1>
    <hr>
    {{name}}同学（学号：{{stuId}}），欢迎选书！
    <!--
    <b-btn v-b-popover.hover="'I am popover content!'" title="Popover Title">aaa</b-btn>
    -->
    <b-table striped hover :items="items" :fields="fields">
      <template slot="show_details" slot-scope="row">
        <b-button size="sm" @click.stop="row.toggleDetails" class="mr-2" variant="info">
          {{ row.detailsShowing ? '隐藏' : '展示' }}信息
        </b-button>
      </template>

      <template slot="row-details" slot-scope="row">
        <b-card>
          <b-row class="mb-2">
            <b-col sm="3" class="text-sm-right"><b>全部作者:</b></b-col>
            <b-col>{{ row.item.authors }}</b-col>
          </b-row>
          <b-row class="mb-2">
            <b-col sm="3" class="text-sm-right"><b>其他描述:</b></b-col>
            <b-col>{{ row.item.detailInformation }}</b-col>
          </b-row>        
        </b-card>
      </template>
      <template slot="action" slot-scope="row">
        <b-form-input size="sm" v-model="nums[row.index]"
          type="text"
          placeholder="0"
          style="width:45px"></b-form-input>
      </template>
    </b-table>
    <p align="right">
    <b-button @click="submitBookInformation">提交书单</b-button>
    <b-button variant="warning">暂存书单</b-button>
    </p>
    </body>
  </div>
</div>
</template>

<script>
import Navbar from './Navbar.vue'
import ajax from '../ajax'
export default {
  name: 'selectbook',
  components: {'my-navbar': Navbar},
  data () {
    return {
      fields: [{key:'name',label:'书名'},
              {key:'author',label:'第一作者'},
              {key:'publisher',label:'出版社'},
              {key:'price',label:'价格'},
              {key:'show_details',label:'详细信息'},
              {key:'action',label:'数量'}],
      
      items:  [
        //{ name: '信号与系统', author: '奥本海姆', authors: 'Alan V. Oppenheim, S.Wilsky',publisher: '机械工业出版社', price: '99', detailInformation:'Hello world.' },
        //{ name: '计算机组成', author: '戴维·帕特森', authors: 'David Patterson, John Hennesey',publisher: '电子工业出版社', price: '80', detailInformation:'Hello world.' }
      ],
      nums: [1,2],
      stuId: '',
      name: '',
      class: ''
    }
  },
  created(){
    this.showCookie();
    this.fetchBookInformation();
  },
  methods:{
    showCookie(){
      //console.log(this.$cookies.keys());
      this.stuId = this.$cookies.get("stuId");
      this.name = this.$cookies.get("name");
      this.name = new Buffer(this.name, 'base64').toString('UTF8');
      this.class = this.$cookies.get("class");
    },
    fetchBookInformation(){
      ajax.ajaxGet('/api/get_student_books', res=>{
        this.items = res.data;
      });
    },
    submitBookInformation(){
      var books = this.items.map(x=>{return {bookid:x.bid};});
      for(var i = 0; i < books.length; i++){
        books[i]['num'] = this.nums[i];
        books[i]['stuId'] = this.stuId;
        books[i]['class'] = this.class;
      }
      ajax.ajaxPost('/api/save_student_books', books);
    }
  }
}
</script>

<style>
.container{
  padding-top: 60px;
}
</style>
