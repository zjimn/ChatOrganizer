# ChatGPT 对话管理器

这是一个基于 Python 开发的窗口应用软件，用于调用微软云平台的 OpenAI 接口与 ChatGPT 进行对话管理。该应用解决了 ChatGPT 原生对话记录分类不便的问题，提供了便捷的目录管理和对话分类功能。

## 功能特点

- **目录管理**：创建、编辑、移动目录，方便分类管理对话记录。
- **对话记录**：所有对话记录保存在 SQLite 数据库中，支持查看搜索编辑和删除。
- **多种内容类型**：支持文本和图片内容的生成与保存。
- **便捷操作**：
  - 在左侧面板添加和选择目录，关联相应的对话记录。
  - 输入框支持文本输入，按回车或点击“获取回答”与 ChatGPT 进行对话。
  - 弹出窗口显示对话内容，支持内容复制。
  - 列表中新增对话记录，可进行编辑和删除，仅保留最终答案后保存。
- **图片处理**：
  - 选择生成图片内容，查看和放大图片细节。
  - 图片保存在 `data/image` 目录下，便于管理和访问。

## 安装指南

1. **克隆仓库**
   ```bash
   git clone https://github.com/zjimn/ChatOrganizer.git
   cd ChatOrganizer
2. **安装依赖**  
   pip install -r requirements.txt
3. **配置微软云平台 OpenAI 接口**  
   - 在项目根目录下创建 .env 文件。  
   - 添加以下内容：  
     DEPLOYMENT_NAME=你的DEPLOYMENT_NAME(用于文字对话生成)    
     DALLE_DEPLOYMENT_NAME=你的DEPLOYMENT_NAME(用于图片对话生成)  
     API_KEY=你的API_KEY  
     AZURE_ENDPOINT=你的AZURE_ENDPOINT  
     API_VERSION=你的API_VERSION(如2024-06-01)  

4. **运行应用**  
   python main.py

## 使用说明

1. **创建目录**  
   在左侧层级树右键后点击“新增目录”按钮，输入目录名称进行创建。
2. **管理对话**
   - 选择一个目录后，所有在该目录下的对话记录将显示在中间列表区域。
   - 可以对对话进行编辑、移动或删除操作。
3. **进行对话**
   - 在底部的输入框中输入文本，按回车或点击“获取回答”按钮与 ChatGPT 进行对话。
   - 对话内容将在弹出窗口中显示，并自动保存到当前选定的目录中。
4. **生成图片**
   - 选择右下角的下拉列表“图片”选项, 可以通过对话生成图片
   - 生成的图片将保存在 data/image 目录下，可以点击图片查看大图。
5. **搜索与查看**
   - 使用顶部的搜索功能，快速查找历史对话记录。
   - 点击任意对话记录，可以查看详细内容或进行编辑。

## 项目结构
   
   ChatGPT-对话管理器/  
   ├── api  
   │   ├── openai_image_api.py  
   │   └── openai_text_api.py  
   ├── config  
   │   ├── app_config.py  
   │   ├── constant.py  
   │   └── enum.py  
   ├── db  
   │   ├── config.py  
   │   ├── config_data_access.py  
   │   ├── content_data_access.py  
   │   ├── content_hierarchy_access.py  
   │   ├── database.py  
   │   ├── dialogue_data_access.py  
   │   └── models.py  
   ├── event  
   │   ├── editor_tree_manager.py  
   │   ├── event_bus.py  
   │   ├── input_manager.py  
   │   ├── list_editor.py  
   │   ├── list_manager.py  
   │   ├── main_manager.py  
   │   ├── output_manager.py  
   │   └── tree_manager.py  
   ├── main.py  
   ├── requirements.txt  
   ├── res  
   │   └── icon  
   │       ├── folder_close.png  
   │       └── folder_open.png  
   ├── service  
   │   └── content_service.py  
   ├── ui  
   │   ├── directory_tree.py  
   │   ├── display_frame.py  
   │   ├── editor_directory_tree.py  
   │   ├── input_frame.py  
   │   ├── main_window.py  
   │   ├── output_window.py  
   │   ├── scrollable_frame.py  
   │   └── syle  
   │       └── tree_view_style_manager.py  
   └── util  
       ├── ImageViewer.py  
       ├── image_util.py  
       ├── str_util.py  
       ├── text_inserter.py  
       ├── token_management.py  
       └── window_util.py