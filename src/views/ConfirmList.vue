<template>
  <div>
  <my-navbar></my-navbar>
  <div class="container">
    <body>
    <h1 align="left">确认生成书单</h1>
    <hr>
    <!--{{name}}同学（学号：{{stuId}}），欢迎选书！-->
    你好，管理员大人
    <!--
    <b-btn v-b-popover.hover="'I am popover content!'" title="Popover Title">aaa</b-btn>
    -->
     <b-card no-body>
      <b-tabs small card v-model="tabIndex">
        <b-tab title="设置筛选条件">
            <b-form-group id="academyInputGroup"
                    label="学院:"
                    label-for="academyInput">
                <b-form-select id="academyInput"
                      :options="academies"
                      required
                      v-model="form.academy">
                </b-form-select>
             </b-form-group>

            <b-form-group id="classInputGroup"
                    label="年级:"
                    label-for="GradeInput">
                <b-form-input id="GradeInput"
                      type="text"
                      v-model="form.class"
                      required
                      placeholder="如F16">
                </b-form-input>
            </b-form-group>

        </b-tab>
        <b-tab title="查看班级列表">
          I'm the second tab
          <b-table striped hover :items="items" :fields="fields">
            <template slot="show_details" slot-scope="row">

                <b-button size="sm"  @click.stop="jumpclass(row.item.id)" class="mr-2" variant="info">
                {{ row.detailsShowing ? '隐藏' : '展示' }}书单
                </b-button>

            </template>
          </b-table>
        </b-tab>
        <b-tab title="查看书单">

            <b-card>
                <!-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-->

                <b-table striped hover :items="classitems" :fields="bookfields">
                    <template slot="action" slot-scope="row">
                        <!--b-button size="sm" @click.stop="row.toggleDetails" class="mr-2" variant="info">
                        添加教材
                        </b-button-->
                       <b-btn size="sm" v-b-modal="'CS_'+row.index" variant="info">添加教材</b-btn>
                       <b-modal :id="'CS_'+row.index" title="书籍添加">
                            <p class="my-4">{{classitems[row.index].course}}添加教材：</p>
                                <b-form-group id="booknameInputGroup"
                                            label="书名:"
                                            label-for="booknameInput">
                                <b-form-input id="booknameInput"
                                                type="text"
                                                v-model="bookname"
                                                required
                                                >
                                </b-form-input>
                                </b-form-group>

                                <b-form-group id="bookEditionInputGroup"
                                            label="版次:"
                                            label-for="bookEditionInput">
                                <b-form-input id="bookEditionInput"
                                                type="text"
                                                v-model="bookedition"
                                                required
                                                >
                                </b-form-input>
                                </b-form-group>

                                <b-form-group id="bookAuthorInputGroup"
                                            label="作者:"
                                            label-for="bookAuthorInput">
                                <b-form-input id="bookAuthorInput"
                                                type="text"
                                                v-model="bookauthor"
                                                required
                                                >
                                </b-form-input>
                                </b-form-group>

                                <b-form-group id="bookPublisherInputGroup"
                                            label="出版社:"
                                            label-for="bookPublisherInput">
                                <b-form-input id="bookPublisherInput"
                                                type="text"
                                                v-model="bookpublisher"
                                                required
                                                >
                                </b-form-input>
                                </b-form-group>

                                <b-form-group id="detailInformationInputGroup"
                                            label="详细信息:"
                                            label-for="detailInformationInput">
                                <b-form-input id="detailInformationInput"
                                                type="text"
                                                v-model="bookdetailInformation"
                                                required
                                                >
                                </b-form-input>
                                </b-form-group>
                        <div slot="modal-footer">
                        <b-btn variant="primary" @click="addBook(classitems[row.index]);hideModal('CS_'+row.index);">添加</b-btn>
                        </div>
                        </b-modal>
                                        
                    </template>
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


                    <template slot="deletaction" slot-scope="row">
                        <!--b-btn v-b-modal="'BK_'+i" variant="outline-success">{{book['name']}}</b-btn-->
                        <b-btn size="sm" v-b-modal="'BK_'+row.index" variant="info">修改教材</b-btn>
                            <b-modal :id="'BK_'+row.index" title="书籍修改">
                                <b-form-group id="booknameInputGroup"
                                            label="书名:"
                                            label-for="booknameInput">
                                <b-form-input id="booknameInput"
                                                type="text"
                                                v-model="classitems[row.index]['name']"
                                                required
                                                >
                                </b-form-input>
                                </b-form-group>

                                <b-form-group id="bookEditionInputGroup"
                                            label="版次:"
                                            label-for="bookEditionInput">
                                <b-form-input id="bookEditionInput"
                                                type="text"
                                                v-model="classitems[row.index]['edition']"
                                                required
                                                >
                                </b-form-input>
                                </b-form-group>

                                <b-form-group id="bookAuthorInputGroup"
                                            label="作者:"
                                            label-for="bookAuthorInput">
                                <b-form-input id="bookAuthorInput"
                                                type="text"
                                                v-model="classitems[row.index]['authors']"
                                                required
                                                >
                                </b-form-input>
                                </b-form-group>

                                <b-form-group id="bookPublisherInputGroup"
                                            label="出版社:"
                                            label-for="bookPublisherInput">
                                <b-form-input id="bookPublisherInput"
                                                type="text"
                                                v-model="classitems[row.index]['publisher']"
                                                required
                                                >
                                </b-form-input>
                                </b-form-group>

                                <b-form-group id="detailInformationInputGroup"
                                            label="详细信息:"
                                            label-for="detailInformationInput">
                                <b-form-input id="detailInformationInput"
                                                type="text"
                                                v-model="classitems[row.index]['detailinformation']"
                                                required
                                                >
                                </b-form-input>
                                </b-form-group>
                        <div slot="modal-footer">
                        <b-btn @click="updateBook(classitems[row.index]);hideModal('BK_'+row.index);">提交</b-btn>
                        </div>       
                        </b-modal>

                    </template>

                </b-table>

                <!-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-->
            <b-button size="sm" @click.stop="tabIndex--" class="mr-2" variant="info">
            确认 <!--!!!!TODO,改动作链接-->
            </b-button>       
            </b-card>
        
           
            <!-- TABLE ---------------------------------------------------内部-->
        </b-tab>
      </b-tabs>
    </b-card>

    <!-- Control buttons-->
    <div class="text-center">
      <b-button-group class="mt-2">
        <b-btn @click="tabIndex--">Previous</b-btn>
        <b-btn @click="tabIndex++">Next</b-btn>
      </b-button-group>
      <br>
      <!--span class="text-muted">Current Tab: {{tabIndex}}</span-->
    </div>
   
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
      tabIndex: 0,
      form: {
        academy: null,
        checked: []
      },
      academies: [
        { text: '选择一个学院', value: null },
        '电子信息与电气工程学院', '机械与动力工程学院', '船舶海洋与建筑工程学院', '致远学院'
      ],
      fields: [{key:'id',label:'班号'},
                 {key:'show_details',label:'展示书单'}
      ],
      
      //courseitems:  [
      //  {name:'电路与电子学', bsid:'1', code:'EI234', books:[]},
      //  {name:'计算机组成', bsid:'2', code:'EI332', books:[]}
      //],

      items:  [
        //{ name: '信号与系统', author: '奥本海姆', authors: 'Alan V. Oppenheim, S.Wilsky',publisher: '机械工业出版社', price: '99', detailInformation:'Hello world.' },
        //{ name: '计算机组成', author: '戴维·帕特森', authors: 'David Patterson, John Hennesey',publisher: '电子工业出版社', price: '80', detailInformation:'Hello world.' }
        {id:'F1603022'},
        {id:'F1603023'}
      ],

      bookfields: [{key:'course',label:'课名'},
              {key:'name',label:'书名'},
              {key:'author',label:'第一作者'},
              {key:'publisher',label:'出版社'},
              {key:'price',label:'价格'},
              {key:'show_details',label:'详细信息'},
              {key:'action',label:'添加'},
              {key:'deletaction',label:'修改'}
              ],

      classitems:  [ //一个班级所对应的所有书
        { bsid:111 ,name: '信号与系统', author: '奥本海姆', authors: 'Alan V. Oppenheim, S.Wilsky',publisher: '机械工业出版社', price: '99', detailInformation:'Hello world.' }
      ],
      nums: [1,2],
      stuId: '',
      name: '',
      class: '',
      //!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! add book
      bookname: '',
      bookpublisher: '',
      bookedition: '',
      bookauthor: '',
      bookdetailInformation: ''
      //!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
        //this.items = res.data;
      });
    },
    addBook(courseitem){
      var curbook = {};
      curbook['name'] = this.bookname;
      curbook['authors'] = this.bookauthor;
      curbook['edition'] = this.bookedition;
      curbook['publisher'] = this.bookpublisher;
      curbook['detailInformation'] = this.bookdetailInformation;
      //curbook['bsid'] = courseitem.bsid
      curbook['course'] = courseitem.course
      this.classitems.push(curbook);
      this.name = '';
      this.authors = '';
      this.edition = '';
      this.publisher = '';
      var book_to_add = {book: curbook, courseid:courseitem.bsid};
      ajax.ajaxPost('/api/save_course_books', book_to_add, res=>{
        var len = courseitem.books.length;
        courseitem.books[len-1]['id'] = res.data.id;
      });
    },
    updateBook(book){
        
      ajax.ajaxPost('/api/update_course_books', book); ///!!!!!!!!!!!!!!这里多了bsid
    },
    submitBookInformation(){
      var books = this.items.map(x=>{return {bookid:x.bid};});
      for(var i = 0; i < books.length; i++){
        books[i]['num'] = this.nums[i];
        books[i]['stuId'] = this.stuId;
        books[i]['class'] = this.class;
      }
      ajax.ajaxPost('/api/save_student_books', books);
    },
    jumpclass(id){
        ajax.ajaxGetWithParam('http://localhost:88/api/get_class_books', {params:{'class':id}}, res=>{
        //this.classitems = res.data;
        //this.nums = res.data.map(x=>x.num);
        this.tabIndex++;
      });
    },
    hideModal(id){
      this.$root.$emit('bv::hide::modal',id);  //发消息关掉模态框
    }
  }
}
</script>

<style>
.container{
  padding-top: 60px;
}
</style>
