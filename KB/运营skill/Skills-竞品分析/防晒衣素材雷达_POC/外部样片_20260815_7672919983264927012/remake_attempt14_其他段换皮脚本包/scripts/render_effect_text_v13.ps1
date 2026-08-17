$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot

try {
    $filter = @'
[2:v]format=rgba,fade=t=in:st=4.45:d=0.12:alpha=1,fade=t=out:st=8.43:d=0.12:alpha=1[t2];
[3:v]format=rgba,fade=t=in:st=8.90:d=0.12:alpha=1,fade=t=out:st=12.18:d=0.12:alpha=1[t3];
[4:v]format=rgba,fade=t=in:st=12.65:d=0.12:alpha=1,fade=t=out:st=17.23:d=0.12:alpha=1[t4];
[5:v]format=rgba,fade=t=in:st=17.75:d=0.12:alpha=1,fade=t=out:st=21.58:d=0.12:alpha=1[t5];
[6:v]format=rgba,fade=t=in:st=22.10:d=0.12:alpha=1,fade=t=out:st=25.43:d=0.12:alpha=1[t6];
[7:v]format=rgba,fade=t=in:st=27.15:d=0.12:alpha=1,fade=t=out:st=28.63:d=0.12:alpha=1[t7];
[0:v][t2]overlay=x=0:y='58+if(lt(t-4.45,0.14),(0.14-(t-4.45))/0.14*18,0)':enable='between(t,4.45,8.55)'[v2];
[v2][t3]overlay=x=0:y='58+if(lt(t-8.90,0.14),(0.14-(t-8.90))/0.14*18,0)':enable='between(t,8.90,12.30)'[v3];
[v3][t4]overlay=x=0:y='970+if(lt(t-12.65,0.14),(0.14-(t-12.65))/0.14*18,0)':enable='between(t,12.65,17.35)'[v4];
[v4][t5]overlay=x=0:y='58+if(lt(t-17.75,0.14),(0.14-(t-17.75))/0.14*18,0)':enable='between(t,17.75,21.70)'[v5];
[v5][t6]overlay=x=0:y='58+if(lt(t-22.10,0.14),(0.14-(t-22.10))/0.14*18,0)':enable='between(t,22.10,25.55)'[v6];
[v6][t7]overlay=x=0:y='4+if(lt(t-27.15,0.14),(0.14-(t-27.15))/0.14*12,0)':enable='between(t,27.15,28.75)'[vout];
[0:a]asplit=2[base_head][base_tail];
[base_head]atrim=start=0:end=27.30,asetpts=PTS-STARTPTS[head];
[base_tail]atrim=start=15.00:end=16.70,asetpts=PTS-STARTPTS[tail];
[head][tail]acrossfade=d=0.10:c1=tri:c2=tri,atrim=duration=28.90[aout]
'@ -replace "`r?`n", ''

    $ffmpegArgs = @(
        '-y', '-hide_banner',
        '-i', 'output\final\军训粉底肤无痕内衣_完整换皮成片_V10_去水印原视频声道.mp4',
        '-framerate', '30', '-loop', '1', '-i', 'overlays\effect_text_v01\T01_军训显痕.png',
        '-framerate', '30', '-loop', '1', '-i', 'overlays\effect_text_v01\T02_学姐安利.png',
        '-framerate', '30', '-loop', '1', '-i', 'overlays\effect_text_v01\T03_跑跳无痕.png',
        '-framerate', '30', '-loop', '1', '-i', 'overlays\effect_text_v01\T04_平整杯面.png',
        '-framerate', '30', '-loop', '1', '-i', 'overlays\effect_text_v01\T05_冰丝透气.png',
        '-framerate', '30', '-loop', '1', '-i', 'overlays\effect_text_v01\T06_白T无痕.png',
        '-framerate', '30', '-loop', '1', '-i', 'overlays\effect_text_v01\T07_军训必备.png',
        '-filter_complex', $filter,
        '-map', '[vout]', '-map', '[aout]',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-ac', '2',
        '-t', '28.90', '-movflags', '+faststart',
        'output\final\军训粉底肤无痕内衣_完整换皮成片_V14_原声特效字_结构避脸_结尾不复读.mp4'
    )

    & ffmpeg @ffmpegArgs
    if ($LASTEXITCODE -ne 0) {
        throw "ffmpeg failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
