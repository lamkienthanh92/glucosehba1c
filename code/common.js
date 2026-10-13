const fs=require('fs');
const D=require('docx'); const {Paragraph,TextRun,Table,TableRow,TableCell,WidthType,ShadingType,AlignmentType,BorderStyle,ImageRun,VerticalAlign}=D;
const FONT='Times New Roman';
const f=(x,d=2)=>Number(x).toFixed(d); const th=n=>Number(n).toLocaleString('en-US'); const sg=(x,d=1)=>(Number(x)>0?'+':Number(x)<0?'−':'')+Math.abs(Number(x)).toFixed(d);
function runs(text,base={}){text=text.replace(/(^|[\s(;,])-(?=\d)/g,'$1−');const out=[];const re=/((?<![\p{L}\d])(?:p|n|r)(?=\s?[=<>])|(?<![\p{L}])(?:SD)(?![\p{L}]))/gu;let last=0,m;
 while((m=re.exec(text))){if(m.index>last)out.push(new TextRun({text:text.slice(last,m.index),font:FONT,size:24,...base}));out.push(new TextRun({text:m[0],font:FONT,size:24,...base,italics:true}));last=m.index+m[0].length;}
 if(last<text.length)out.push(new TextRun({text:text.slice(last),font:FONT,size:24,...base}));return out;}
function mk(REF){
 const order=[];
 const R=(text)=>text.replace(/\{([A-Za-z0-9,]+)\}/g,(m,ks)=>{const nums=ks.split(',').map(k=>{if(!REF[k])throw new Error('ref '+k);let i=order.indexOf(k);if(i<0){order.push(k);i=order.length-1;}return i+1;}).sort((a,b)=>a-b);
   const parts=[];let st=nums[0],pr=nums[0];for(let i=1;i<=nums.length;i++){if(nums[i]===pr+1){pr=nums[i];continue;}parts.push(st===pr?`${st}`:(pr===st+1?`${st},${pr}`:`${st}–${pr}`));st=nums[i];pr=nums[i];}
   return '['+parts.join(',')+']';});
 return {R,order};
}
const P=(t,o={})=>new Paragraph({alignment:o.align??AlignmentType.JUSTIFIED,spacing:{line:o.line??360,after:o.after??100,before:o.before??0},indent:o.indent?{firstLine:400}:undefined,keepNext:o.keepNext,children:o.hl?[new TextRun({text:t,font:FONT,size:24,highlight:'yellow'})]:runs(t,{size:o.size||24,bold:o.bold,italics:o.italics})});
const PL=(label,t,o={})=>new Paragraph({alignment:AlignmentType.JUSTIFIED,spacing:{line:o.line??360,after:100},children:[new TextRun({text:label,font:FONT,size:24,bold:true}),...runs(t,{size:24})]});
const H=(t,l=1)=>new Paragraph({spacing:{line:360,before:l===1?240:140,after:80},keepNext:true,children:[new TextRun({text:t,font:FONT,size:l===1?26:24,bold:true,italics:l===2})]});
const thin={style:BorderStyle.SINGLE,size:4,color:'000000'},none={style:BorderStyle.NONE,size:0,color:'FFFFFF'};
function cell(t,w,o={}){return new TableCell({width:{size:w,type:WidthType.DXA},columnSpan:o.span,verticalAlign:VerticalAlign.CENTER,margins:{top:30,bottom:30,left:60,right:60},
 shading:o.fill?{fill:o.fill,type:ShadingType.CLEAR,color:'auto'}:undefined,borders:{top:o.top?thin:none,bottom:o.bottom?thin:none,left:none,right:none},
 children:[new Paragraph({alignment:o.left?AlignmentType.LEFT:AlignmentType.CENTER,children:runs(t,{size:19,bold:!!o.bold})})]})}
const TW=9070;
const tbl=(W,head,rows)=>new Table({width:{size:TW,type:WidthType.DXA},columnWidths:W,rows:[
 new TableRow({tableHeader:true,children:head.map((h,j)=>cell(h,W[j],{bold:true,left:j===0,top:true,bottom:true}))}),
 ...rows.map((r,i)=>r.sec?new TableRow({cantSplit:true,children:[cell(r.sec,TW,{span:W.length,left:true,bold:true,fill:'EDEDED'})]}):new TableRow({cantSplit:true,children:r.map((t,j)=>cell(t,W[j],{left:j===0,bottom:i===rows.length-1}))}))]});
const cap=(a,b)=>new Paragraph({spacing:{line:300,before:160,after:60},keepNext:true,children:[new TextRun({text:a,font:FONT,size:22,bold:true}),...runs(b,{size:22})]});
const note=(t)=>new Paragraph({spacing:{line:260,after:30},children:runs(t,{size:19})});
const img=(file,w,h)=>new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:140,after:40},keepNext:true,children:[new ImageRun({type:'png',data:fs.readFileSync(file),transformation:{width:w,height:h},altText:{title:file,description:file,name:file}})]});
const figcap=(a,b)=>new Paragraph({spacing:{line:280,after:200},alignment:AlignmentType.JUSTIFIED,children:[new TextRun({text:a,font:FONT,size:22,bold:true}),...runs(b,{size:22})]});
module.exports={D,FONT,f,th,sg,runs,mk,P,PL,H,cell,TW,tbl,cap,note,img,figcap};
