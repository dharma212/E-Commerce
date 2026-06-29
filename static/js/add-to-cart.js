// let defaultProductImage = "";

// document.addEventListener("click", function(e){
//     const btn = e.target.closest(".add-to-cart");
//     if(!btn) return;

//     e.preventDefault();

//     const hasColors = btn.dataset.colors && btn.dataset.colors.trim() !== "";
//     const hasSizes = btn.dataset.sizes && btn.dataset.sizes.trim() !== "";

//     if(!hasColors && !hasSizes){
//         return;
//     }

//     e.preventDefault();
//     e.stopImmediatePropagation();

//     popupProductId = btn.dataset.id;
//     document.getElementById("popupProductName").innerText = btn.dataset.name;

//     let mainProductImg = btn.dataset.image;
//     if(!mainProductImg || mainProductImg === "" || mainProductImg.includes("None")) {
//         const productCard = btn.closest(".product-item, .card, .product-card");
//         if(productCard) {
//             const cardImg = productCard.querySelector("img");
//             if(cardImg) mainProductImg = cardImg.src;
//         }
//     }
//     defaultProductImage = mainProductImg || "/static/img/no-image.png";
//     document.getElementById("popupProductImage").src = defaultProductImage;

//     const colorsDiv = document.getElementById("popupColors");
//     const sizesDiv = document.getElementById("popupSizes");

//     colorsDiv.innerHTML = "";
//     sizesDiv.innerHTML = "";

//     let colorImageMap = {};
//     if (btn.dataset.colorImages) {
//         btn.dataset.colorImages.split(",").forEach(item => {
//             const parts = item.split(":");
//             if (parts.length >= 2) {
//                 const cName = parts[0].trim().toLowerCase();
//                 const cUrl = parts.slice(1).join(":").trim(); 
//                 if(cName && cUrl) {
//                     colorImageMap[cName] = cUrl;
//                 }
//             }
//         });
//     }

//     (btn.dataset.colors || "").split(",").forEach(color => {
//         color = color.trim();
//         if(color){
//             const lowerColor = color.toLowerCase();
//             const finalColorImg = colorImageMap[lowerColor] ? colorImageMap[lowerColor] : defaultProductImage;

//             colorsDiv.innerHTML += `
//                 <span class="variant-option" data-color-img="${finalColorImg}">
//                     <img src="${finalColorImg}" alt="${color}" onerror="this.src='${defaultProductImage}'">
//                     ${color}
//                 </span>
//             `;
//         }
//     });

//     (btn.dataset.sizes || "").split(",").forEach(size=>{
//         size = size.trim();
//         if(size){
//             sizesDiv.innerHTML += `
//                 <span class="variant-option">
//                     ${size}
//                 </span>
//             `;
//         }
//     });

//     document.getElementById("variantPopup").style.display = "flex";
// });

// document.addEventListener("click", function(e){
//     const targetOption = e.target.closest(".variant-option");
//     if(targetOption){
//         const parent = targetOption.parentElement;
//         parent.querySelectorAll(".variant-option").forEach(x=>{
//             x.classList.remove("active");
//         });
//         targetOption.classList.add("active");

//         if(parent.id === "popupColors") {
//             const newImgSrc = targetOption.dataset.colorImg;
//             if(newImgSrc) {
//                 document.getElementById("popupProductImage").src = newImgSrc;
//             }
//         }
//     }
// });

// function closeVariantPopup(){
//     document.getElementById("variantPopup").style.display = "none";
// }