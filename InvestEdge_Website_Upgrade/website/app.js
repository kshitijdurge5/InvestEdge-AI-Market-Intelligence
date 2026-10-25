const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const gainers = [
 {symbol:"R",name:"Reliance Industries",code:"RELIANCE",price:"₹1,462.80",change:"+2.41%",up:true},
 {symbol:"T",name:"Tata Motors",code:"TATAMOTORS",price:"₹718.25",change:"+1.86%",up:true},
 {symbol:"I",name:"Infosys",code:"INFY",price:"₹1,548.10",change:"+1.34%",up:true},
 {symbol:"L",name:"Larsen & Toubro",code:"LT",price:"₹3,682.00",change:"+0.98%",up:true},
 {symbol:"H",name:"HDFC Bank",code:"HDFCBANK",price:"₹962.45",change:"+0.74%",up:true}
];
const losers = [
 {symbol:"A",name:"Asian Paints",code:"ASIANPAINT",price:"₹2,814.20",change:"−1.92%",up:false},
 {symbol:"B",name:"Bajaj Finance",code:"BAJFINANCE",price:"₹8,924.50",change:"−1.31%",up:false},
 {symbol:"T",name:"TCS",code:"TCS",price:"₹4,012.10",change:"−0.88%",up:false},
 {symbol:"W",name:"Wipro",code:"WIPRO",price:"₹522.40",change:"−0.65%",up:false},
 {symbol:"M",name:"Maruti Suzuki",code:"MARUTI",price:"₹12,640.00",change:"−0.42%",up:false}
];
function renderMovers(which="gainers"){const data=which==="gainers"?gainers:losers;$("#moversList").innerHTML=data.map(x=>`<div class="mover-row"><div class="stock-symbol">${x.symbol}</div><div><div class="stock-name">${x.name}</div><div class="stock-code">${x.code}</div></div><div><div class="stock-price">${x.price}</div><div class="stock-change ${x.up?"positive":"negative"}">${x.change}</div></div></div>`).join("");}
renderMovers();
$$("[data-movers]").forEach(b=>b.addEventListener("click",()=>{$$("[data-movers]").forEach(x=>x.classList.toggle("selected",x===b));renderMovers(b.dataset.movers)}));
const titles={overview:"Market overview",stocks:"Stocks",funds:"Mutual funds",sip:"SIP planner",bonds:"Bonds",etfs:"ETFs",crypto:"Crypto watch",ipos:"IPO tracker",portfolio:"Portfolio overview",news:"Market news",research:"AI research"};
function toast(msg){const t=$("#toast");t.textContent=msg;t.classList.add("show");clearTimeout(window.toastTimer);window.toastTimer=setTimeout(()=>t.classList.remove("show"),2600)}
function navigate(view){$("#pageTitle").textContent=titles[view]||"Market overview";$$(".nav-item").forEach(b=>b.classList.toggle("active",b.dataset.view===view));$("#sidebar").classList.remove("open");if(view!=="overview")toast(`${titles[view]} preview selected — detailed module is being built.`);if(view==="research")$("#researchInput").focus()}
$$(".nav-item").forEach(b=>b.addEventListener("click",()=>navigate(b.dataset.view)));
$$("[data-view-link]").forEach(b=>b.addEventListener("click",()=>navigate(b.dataset.viewLink)));
$("#menuBtn").addEventListener("click",()=>$("#sidebar").classList.toggle("open"));
const chartData={
 "1D":{value:"24,695.35",change:"▲ 0.62%",d:"M0 175 L40 162 L80 170 L120 130 L160 143 L200 110 L240 122 L280 84 L320 100 L360 66 L400 91 L440 50 L480 65 L520 44 L560 57 L600 28 L640 40 L700 17"},
 "1W":{value:"24,695.35",change:"▲ 1.84%",d:"M0 185 L40 173 L80 160 L120 180 L160 140 L200 150 L240 120 L280 134 L320 92 L360 112 L400 83 L440 97 L480 60 L520 71 L560 47 L600 57 L640 30 L700 17"},
 "1M":{value:"24,695.35",change:"▲ 3.21%",d:"M0 200 L40 175 L80 190 L120 158 L160 166 L200 130 L240 143 L280 104 L320 123 L360 88 L400 102 L440 75 L480 83 L520 52 L560 68 L600 42 L640 48 L700 17"},
 "1Y":{value:"24,695.35",change:"▲ 8.46%",d:"M0 210 L40 195 L80 178 L120 188 L160 152 L200 165 L240 132 L280 143 L320 109 L360 120 L400 83 L440 100 L480 68 L520 76 L560 43 L600 55 L640 31 L700 17"}
};
$$("[data-range]").forEach(b=>b.addEventListener("click",()=>{const d=chartData[b.dataset.range];$$("[data-range]").forEach(x=>x.classList.toggle("selected",x===b));$("#chartValue").textContent=d.value;$("#chartChange").textContent=d.change;$("#chartLine").setAttribute("d",d.d);$("#chartArea").setAttribute("d",d.d+" L700 220 L0 220 Z");}));
function runResearch(){const val=$("#researchInput").value.trim();if(!val){$("#researchInput").focus();toast("Enter a topic to research first.");return}const result=$("#researchResult");result.hidden=false;result.innerHTML=`<strong>Research preview</strong><br>For “${val.replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}”, start by defining your goal, time horizon and ability to tolerate losses. Compare fees, diversification, liquidity and downside scenarios before making a decision. This demo does not access live data or provide personalised advice.`;result.scrollIntoView({behavior:"smooth",block:"nearest"})}
$("#researchBtn").addEventListener("click",runResearch);$("#researchInput").addEventListener("keydown",e=>{if(e.key==="Enter")runResearch()});$$("[data-prompt]").forEach(b=>b.addEventListener("click",()=>{$("#researchInput").value=b.dataset.prompt;runResearch()}));
$$("footer a").forEach(a=>a.addEventListener("click",e=>{e.preventDefault();toast("Legal and support pages will be connected before public launch.")}));
