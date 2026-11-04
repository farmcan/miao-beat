import './compat.js';
import {boot} from './store.js';
boot().then(()=>import('../../public/app.js')).catch(()=>{document.getElementById('soundStatus').textContent='启动未完成，请关闭小工具重新打开。';});
