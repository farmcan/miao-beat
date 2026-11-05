import './compat.js';
import {mountLayout} from './layout.js';
import {boot} from './store.js';
boot().then(()=>import('../../public/app.js')).then(()=>mountLayout(document)).catch(()=>{document.getElementById('soundStatus').textContent='启动未完成，请关闭小工具重新打开。';});
