import{_ as h}from"./Layout-ktRl6OHX.js";import{r as x,N as b,e as t,f as a,h as w,j as o,k as e,l,v as c,x as v,z as d,u as i,F as y}from"./index-CM53D1dc.js";const g={class:"mx-auto px-4 lg:px-8 max-w-[1800px]"},k={class:"flex flex-col lg:flex-row justify-between items-center my-6"},F=e("div",null,[e("h3",{class:"text-3xl"},"planner")],-1),D={class:"flex flex-wrap -m-2"},V={class:"flex flex-col bg-white p-4 rounded gap-2 w-full",style:{color:"{{ dashboard.color }}"}},j={class:"flex justify-between items-center"},B={class:"text-xs font-semibold"},C={class:"flex justify-start items-center"},N={class:"text-base"},S={__name:"Dashboard",setup(z){let m=[{label:"Dashboard",route:{name:"Dashboard"}}];const r=x(""),_=b({doctype:"Planner Dashboard",fields:["dashboard_name","color","show_employee_holidays","department"],auto:!0});return(I,n)=>{const u=t("FeatherIcon"),p=t("FormControl"),f=t("router-link");return a(),w(h,{breadcrumbs:i(m)},{default:o(()=>[e("div",g,[e("div",k,[F,l(p,{type:"text",size:"lg",variant:"outline",placeholder:"Search...",disabled:!1,modelValue:r.value,"onUpdate:modelValue":n[0]||(n[0]=s=>r.value=s),class:"w-full lg:w-2/12"},{suffix:o(()=>[l(u,{class:"w-4",name:"search"})]),_:1},8,["modelValue"])]),e("div",D,[(a(!0),c(y,null,v(i(_).data,s=>(a(),c("div",{class:"w-3/12 lg:w-1/4 p-2",key:s.dashboard_name},[l(f,{to:{name:"Planner",params:{dashboardName:s.dashboard_name,department:s.department}}},{default:o(()=>[e("div",V,[e("div",j,[e("p",B,d(s.dashboard_name),1)]),e("div",C,[e("p",N,d(s.department),1)])])]),_:2},1032,["to"])]))),128))])])]),_:1},8,["breadcrumbs"])}}};export{S as default};