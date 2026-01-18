// 机器人表情逻辑控制
const pupilLeft = document.getElementById('pupil-left');
const pupilRight = document.getElementById('pupil-right');
const lidLeft = document.getElementById('lid-left');
const lidRight = document.getElementById('lid-right');
const mouth = document.getElementById('mouth');

const valMouth = document.getElementById('val-mouth');
const valEye = document.getElementById('val-eye');
const valLid = document.getElementById('val-lid');
const logPanel = document.getElementById('log');
const statusText = document.getElementById('playback-status');

// 映射 21 个眼球位置到 CSS 坐标 (x, y 百分比)
// 我们简化为 5x5 网格映射
function getEyeCoords(id) {
    const row = Math.floor((id - 1) / 5) + 1;
    const col = (id - 1) % 5 + 1;

    // 中心点 (11) 对应 50%, 50%
    const x = 50 + (col - 3) * 20;
    const y = 50 + (row - 3) * 20;
    return { x: `${x}%`, y: `${y}%` };
}

function updateFace(state) {
    const { mouth: m, eye: e, lid: l } = state;

    // 1. 嘴巴 (1-5 档)
    const mouthHeight = [2, 10, 25, 40, 55][m - 1];
    mouth.style.height = `${mouthHeight}px`;
    mouth.style.borderRadius = m === 1 ? '0%' : '50%';
    valMouth.innerText = m;

    // 2. 眼球位置 (1-21 档)
    const coords = getEyeCoords(e);
    pupilLeft.style.left = coords.x;
    pupilLeft.style.top = coords.y;
    pupilRight.style.left = coords.x;
    pupilRight.style.top = coords.y;
    valEye.innerText = e;

    // 3. 眼皮 (1-4 档)
    // 1: 正常(-100%), 2: 眯眼(-50%), 3: 闭眼(0%), 4: 瞪眼(-120%)
    const lidTop = [-100, -55, 0, -125][l - 1];
    lidLeft.style.top = `${lidTop}%`;
    lidRight.style.top = `${lidTop}%`;
    valLid.innerText = l;

    addLog(`执行动作: Mouth=${m}, Eye=${e}, Lid=${l}`);
}

function addLog(msg) {
    const time = new Date().toLocaleTimeString();
    logPanel.innerHTML += `<div>[${time}] ${msg}</div>`;
    logPanel.scrollTop = logPanel.scrollHeight;
}

// 模拟播放序列
async function playSequence(sequence) {
    statusText.innerText = "播放中...";
    for (const frame of sequence) {
        updateFace(frame);
        await new Promise(r => setTimeout(r, frame.duration || 300));
    }
    statusText.innerText = "播放结束";
    addLog("序列播放完成。");
}

// 演示序列
const demoData = [
    { "mouth": 1, "eye": 11, "lid": 1, "duration": 500 },
    { "mouth": 3, "eye": 11, "lid": 1, "duration": 300 },
    { "mouth": 4, "eye": 11, "lid": 1, "duration": 300 },
    { "mouth": 5, "eye": 3, "lid": 4, "duration": 600 }, // 哇！
    { "mouth": 1, "eye": 11, "lid": 3, "duration": 1000 }, // 思考/闭眼
    { "mouth": 1, "eye": 11, "lid": 1, "duration": 500 }
];

document.getElementById('btn-demo').onclick = () => playSequence(demoData);

// 加载预测文件 (契约文件)
document.getElementById('btn-load').onclick = async () => {
    try {
        addLog("正在尝试加载 data/output/prediction.json...");
        const response = await fetch('../../data/output/prediction.json');
        if (!response.ok) throw new Error("文件未找到");
        const data = await response.json();
        playSequence(data);
    } catch (err) {
        addLog(`错误: ${err.message}`);
        alert("尚未生成预测文件，请先运行数据管道。");
    }
};

// 初始化
updateFace({ "mouth": 1, "eye": 11, "lid": 1 });
addLog("等待指令...");
