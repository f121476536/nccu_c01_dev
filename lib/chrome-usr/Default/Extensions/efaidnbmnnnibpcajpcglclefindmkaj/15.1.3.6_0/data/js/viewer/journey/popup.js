/*************************************************************************
* ADOBE CONFIDENTIAL
* ___________________
*
*  Copyright 2015 Adobe Systems Incorporated
*  All Rights Reserved.
*
* NOTICE:  All information contained herein is, and remains
* the property of Adobe Systems Incorporated and its suppliers,
* if any.  The intellectual and technical concepts contained
* herein are proprietary to Adobe Systems Incorporated and its
* suppliers and are protected by all applicable intellectual property laws,
* including trade secret and or copyright laws.
* Dissemination of this information or reproduction of this material
* is strictly forbidden unless prior written permission is obtained
* from Adobe Systems Incorporated.
**************************************************************************/
$((function(){"use strict";let e=null;switch(window.location.search&&window.location.search.includes("fteExperiment")&&(e=window.location.search.split("=")[1]),e){case"dc-cv-fte-helpx-center":$("#fullscreen-fte").removeClass("hidden");break;case"dc-cv-fte-helpx-animated":$(".fteSlider").removeClass("hidden");break;default:$("#popup1").removeClass("hidden")}function t(e,t){const n={main_op:"analytics",analytics:[[e,t]]};util.messageToMain(n)}function n(){var e={content_op:"dismiss",main_op:"relay_to_content",fteUI:!0};util.messageToMain(e)}$(document).on("click","#pdfOwnershipPromptCancel, #pdfOwnershipCenterCancelBtn, #pdfOwnershipSliderCancelBtn",(function(e){switch(e.preventDefault(),this.id){case"pdfOwnershipCenterCancelBtn":t(acom_analytics.e.VIEWER_FTE_CENTER_CANCEL);break;case"pdfOwnershipSliderCancelBtn":t(acom_analytics.e.VIEWER_FTE_ANIMATION_CANCEL);break;default:t(acom_analytics.e.VIEWER_FTE_NOT_NOW)}n()})),$(document).on("click","#pdfOwnershipPromptOk, #pdfOwnershipCenterFTEConfirmBtn, #pdfOwnershipSliderConfirmBtn",(function(e){switch(e.preventDefault(),this.id){case"pdfOwnershipCenterFTEConfirmBtn":t(acom_analytics.e.VIEWER_FTE_CENTER_CONFIRM);break;case"pdfOwnershipSliderConfirmBtn":t(acom_analytics.e.VIEWER_FTE_ANIMATION_CONFIRM);break;default:t(acom_analytics.e.VIEWER_FTE_SET_DEFAULT)}!function(e){if(!e)return void console.log("Error: No value specified");util.setCookie("pdfViewer",e),util.setCookie("fteShow","true")}(!0),n()})),$((function(){util.translateElements(".translate")}));var i=1;setInterval((function(){var e,t,n,a;e=document.getElementsByClassName("slides"),t=document.getElementById("slider").offsetWidth,n=e.length,a=document.getElementById("slideWrap"),i<n?(a.style.left="-"+i*t+"px",i++):i==n&&(a.style.left="0px",i=1)}),3e3)}));