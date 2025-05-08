import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Func1 from '../views/Func1.vue'
import Func2 from '../views/Func2.vue'
import Func3 from '../views/Func3.vue'
import Func4 from '../views/Func4.vue'
import Func5 from '../views/Func5.vue'
import Func6 from '../views/Func6.vue'
import Func7 from '../views/Func7.vue'
import Func8 from '../views/Func8.vue'
import Func9 from '../views/Func9.vue'
import Func10 from '../views/Func10.vue'
import student from '../views/student/analysis.vue'
import KnowledgeOrganization from "../views/Knowledge_Organization.vue";

import PageEditor from '../views/Func1_page/PageEditor.vue'
import PagePreview2 from '@/views/Func1_page/PagePreview2.vue'
import WangEditor from '@/views/tool/WangEditor.vue'
import Test from '../views/Test/test.vue' 
const routes: Array<RouteRecordRaw> = [
  {
    path: '/function1',
    name: 'Function1',
    component: Func1
  },
  {
    path: '/Knowledge_Organization',
    name: 'Knowledge_Organization',
    component: KnowledgeOrganization
  },
  {
    path: '/student',
    name: 'student',
    component: student,
  },
  {
    path: '/function2',
    name: 'Function2',
    component: Func2
  },
  {
    path: '/function3',
    name: 'Function3',
    component: Func3
  },
  {
    path: '/function4',
    name: 'Function4',
    component: Func4
  },
  {
    path: '/function5',
    name: 'Function5',
    component: Func5
  },
  {
    path: '/function6',
    name: 'Function6',
    component: Func6
  },
  {
    path: '/function7',
    name: 'Function7',
    component: Func7
  },
  {
    path: '/function8',
    name: 'Function8',
    component: Func8
  },
  {
    path: '/function9',
    name: 'Function9',
    component: Func9
  },
  {
    path: '/editor',
    name: 'PageEditor',
    component: PageEditor,
  },
  {
    path: '/preview2',
    name: 'PagePreview2',
    component: PagePreview2,
  },
  {
    path: '/wangEditor',
    name: 'WangEditor',
    component: WangEditor,
  },
  {
    path: '/test',
    name: 'Test',
    component: Test
  },
  {
    path: '/function10',
    name: 'Function10',
    component: Func10
  },

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router