// Only runtime features used by the shared web code; ES2017 parsing is handled by esbuild.
if(typeof window.globalThis==='undefined')window.globalThis=window;
if(!Array.prototype.at)Object.defineProperty(Array.prototype,'at',{value:function(i){i=Math.trunc(i)||0;return this[i<0?this.length+i:i];}});
if(!Array.prototype.flatMap)Object.defineProperty(Array.prototype,'flatMap',{value:function(fn){return this.reduce(function(a,v,i){return a.concat(fn(v,i));},[]);}});
if(!Object.hasOwn)Object.hasOwn=function(o,k){return Object.prototype.hasOwnProperty.call(o,k);};
if(!Promise.prototype.finally)Object.defineProperty(Promise.prototype,'finally',{value:function(fn){return this.then(function(v){return Promise.resolve(fn()).then(function(){return v;});},function(e){return Promise.resolve(fn()).then(function(){throw e;});});}});
if(!Element.prototype.replaceChildren)Element.prototype.replaceChildren=function(){while(this.firstChild)this.removeChild(this.firstChild);for(var i=0;i<arguments.length;i++)this.append(arguments[i]);};
