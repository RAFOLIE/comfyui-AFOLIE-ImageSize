import { app } from "../../scripts/app.js";

/**
 * AFOLIE 背景透明化节点 - 颜色选择器组件
 * 提供十六进制输入、颜色选择器色块和吸色器功能
 */
app.registerExtension({
    name: "AFOLIE.BackgroundTransparent",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeType.comfyClass === "AFOLIE背景透明化") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);
                
                // 获取透明色值输入组件
                const colorWidget = this.widgets.find(w => w.name === "透明色值");
                
                if (!colorWidget) {
                    return result;
                }
                
                // 创建自定义颜色选择器容器
                const container = document.createElement("div");
                container.style.display = "flex";
                container.style.alignItems = "center";
                container.style.padding = "5px";
                container.style.gap = "8px";
                
                // 创建十六进制颜色输入框
                const hexInput = document.createElement("input");
                hexInput.type = "text";
                hexInput.value = colorWidget.value || "#ffffff";
                hexInput.placeholder = "#ffffff";
                hexInput.style.width = "80px";
                hexInput.style.height = "28px";
                hexInput.style.padding = "4px 8px";
                hexInput.style.border = "1px solid #555";
                hexInput.style.borderRadius = "4px";
                hexInput.style.backgroundColor = "#333";
                hexInput.style.color = "#fff";
                hexInput.style.fontFamily = "monospace";
                hexInput.style.fontSize = "12px";
                
                // 创建颜色选择器色块
                const colorPicker = document.createElement("input");
                colorPicker.type = "color";
                colorPicker.value = colorWidget.value || "#ffffff";
                colorPicker.style.width = "36px";
                colorPicker.style.height = "28px";
                colorPicker.style.padding = "0";
                colorPicker.style.border = "2px solid #555";
                colorPicker.style.borderRadius = "4px";
                colorPicker.style.cursor = "pointer";
                colorPicker.style.backgroundColor = "transparent";
                colorPicker.title = "点击选择颜色 (色相立方体 & HSB)";
                
                // 创建吸色器按钮
                const eyedropperBtn = document.createElement("button");
                eyedropperBtn.innerHTML = "🎯";
                eyedropperBtn.title = "从屏幕取色";
                eyedropperBtn.style.width = "32px";
                eyedropperBtn.style.height = "28px";
                eyedropperBtn.style.padding = "0";
                eyedropperBtn.style.border = "1px solid #555";
                eyedropperBtn.style.borderRadius = "4px";
                eyedropperBtn.style.backgroundColor = "#444";
                eyedropperBtn.style.color = "#fff";
                eyedropperBtn.style.cursor = "pointer";
                eyedropperBtn.style.fontSize = "14px";
                eyedropperBtn.style.display = "flex";
                eyedropperBtn.style.alignItems = "center";
                eyedropperBtn.style.justifyContent = "center";
                
                // 鼠标悬停效果
                eyedropperBtn.addEventListener("mouseenter", () => {
                    eyedropperBtn.style.backgroundColor = "#555";
                });
                eyedropperBtn.addEventListener("mouseleave", () => {
                    eyedropperBtn.style.backgroundColor = "#444";
                });
                
                // 创建颜色预览标签
                const previewLabel = document.createElement("span");
                previewLabel.style.fontSize = "11px";
                previewLabel.style.color = "#aaa";
                previewLabel.style.marginLeft = "4px";
                previewLabel.textContent = "预览";
                
                // 创建颜色预览块
                const colorPreview = document.createElement("div");
                colorPreview.style.width = "20px";
                colorPreview.style.height = "20px";
                colorPreview.style.borderRadius = "3px";
                colorPreview.style.border = "1px solid #666";
                colorPreview.style.backgroundColor = colorWidget.value || "#ffffff";
                colorPreview.style.boxShadow = "inset 0 0 0 1px rgba(0,0,0,0.1)";
                
                // 验证并格式化十六进制颜色
                const validateHexColor = (hex) => {
                    hex = hex.trim();
                    if (!hex.startsWith('#')) {
                        hex = '#' + hex;
                    }
                    // 支持 3 位和 6 位十六进制
                    const match3 = hex.match(/^#([0-9a-fA-F]{3})$/);
                    const match6 = hex.match(/^#([0-9a-fA-F]{6})$/);
                    
                    if (match3) {
                        // 将 3 位扩展为 6 位
                        const r = match3[1][0];
                        const g = match3[1][1];
                        const b = match3[1][2];
                        return `#${r}${r}${g}${g}${b}${b}`.toLowerCase();
                    }
                    if (match6) {
                        return hex.toLowerCase();
                    }
                    return null;
                };
                
                // 更新所有颜色显示
                const updateColor = (hexColor) => {
                    const validColor = validateHexColor(hexColor);
                    if (validColor) {
                        hexInput.value = validColor;
                        colorPicker.value = validColor;
                        colorPreview.style.backgroundColor = validColor;
                        colorWidget.value = validColor;
                        hexInput.style.borderColor = "#555";
                        
                        // 触发节点更新
                        if (colorWidget.callback) {
                            colorWidget.callback(validColor);
                        }
                        this.setDirtyCanvas(true);
                    } else {
                        hexInput.style.borderColor = "#f44";
                    }
                };
                
                // 十六进制输入框事件
                hexInput.addEventListener("input", (e) => {
                    updateColor(e.target.value);
                });
                
                hexInput.addEventListener("blur", (e) => {
                    const validColor = validateHexColor(e.target.value);
                    if (validColor) {
                        hexInput.value = validColor;
                    } else {
                        // 恢复为上一个有效值
                        hexInput.value = colorWidget.value || "#ffffff";
                        hexInput.style.borderColor = "#555";
                    }
                });
                
                // 颜色选择器事件
                colorPicker.addEventListener("input", (e) => {
                    updateColor(e.target.value);
                });
                
                // 吸色器按钮事件
                eyedropperBtn.addEventListener("click", async () => {
                    if ('EyeDropper' in window) {
                        try {
                            eyedropperBtn.style.backgroundColor = "#666";
                            const eyeDropper = new EyeDropper();
                            const { sRGBHex } = await eyeDropper.open();
                            updateColor(sRGBHex);
                        } catch (e) {
                            // 用户取消或发生错误
                            console.log("吸色器已取消或出错:", e);
                        } finally {
                            eyedropperBtn.style.backgroundColor = "#444";
                        }
                    } else {
                        alert("您的浏览器不支持吸色器功能 (EyeDropper API)");
                    }
                });
                
                // 监听原始 widget 值变化
                const originalCallback = colorWidget.callback;
                colorWidget.callback = (value) => {
                    const validColor = validateHexColor(value);
                    if (validColor) {
                        hexInput.value = validColor;
                        colorPicker.value = validColor;
                        colorPreview.style.backgroundColor = validColor;
                    }
                    if (originalCallback) {
                        originalCallback(value);
                    }
                };
                
                // 组装容器
                container.appendChild(hexInput);
                container.appendChild(colorPicker);
                container.appendChild(eyedropperBtn);
                container.appendChild(previewLabel);
                container.appendChild(colorPreview);
                
                // 添加 DOM 组件到节点
                this.addDOMWidget("color_picker_widget", "color_picker", container, {
                    serialize: false,
                    hideOnZoom: false,
                });
                
                // 隐藏原始的字符串输入框（但保留其功能）
                if (colorWidget.inputEl) {
                    colorWidget.inputEl.style.display = "none";
                }
                
                // 调整节点大小
                this.setSize([280, this.size[1]]);
                
                return result;
            };
        }
    },
});
