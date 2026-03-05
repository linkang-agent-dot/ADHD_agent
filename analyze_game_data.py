import re
from collections import defaultdict

raw_data = """
1	{"game_result":1	level_name:0	main_cfg:101427055	mian_level:18	round_num:1}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:14	round_num:3}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:25	round_num:2}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:26	round_num:1}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:27	round_num:1}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:29	round_num:2}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:30	round_num:1}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:31	round_num:2}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:34	round_num:3}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:36	round_num:1}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:37	round_num:3}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:39	round_num:1}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:39	round_num:2}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:40	round_num:1}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:40	round_num:2}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:41	round_num:3}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:42	round_num:2}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:43	round_num:3}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:44	round_num:2}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:45	round_num:2}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:47	round_num:2}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:49	round_num:1}
1	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:49	round_num:3}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:1	round_num:2}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:16	round_num:3}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:2	round_num:1}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:23	round_num:1}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:24	round_num:1}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:25	round_num:3}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:26	round_num:2}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:27	round_num:1}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:28	round_num:1}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:28	round_num:3}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:30	round_num:2}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:31	round_num:2}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:32	round_num:2}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:33	round_num:2}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:35	round_num:2}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:35	round_num:3}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:37	round_num:1}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:38	round_num:3}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:40	round_num:1}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:42	round_num:3}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:44	round_num:3}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:45	round_num:2}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:48	round_num:2}
1	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:9	round_num:2}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:1	round_num:1}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:17	round_num:3}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:19	round_num:2}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:21	round_num:3}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:24	round_num:1}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:24	round_num:2}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:25	round_num:1}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:26	round_num:3}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:27	round_num:2}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:28	round_num:1}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:28	round_num:2}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:29	round_num:1}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:29	round_num:3}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:31	round_num:2}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:32	round_num:2}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:33	round_num:3}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:34	round_num:2}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:36	round_num:2}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:36	round_num:3}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:38	round_num:1}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:40	round_num:3}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:41	round_num:1}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:43	round_num:1}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:43	round_num:3}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:45	round_num:3}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:46	round_num:2}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:48	round_num:1}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:49	round_num:2}
1	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:9	round_num:2}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:10	round_num:2}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:18	round_num:3}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:20	round_num:2}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:20	round_num:3}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:22	round_num:3}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:24	round_num:3}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:25	round_num:1}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:25	round_num:2}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:26	round_num:1}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:26	round_num:2}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:27	round_num:1}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:27	round_num:3}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:28	round_num:2}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:29	round_num:2}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:30	round_num:3}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:32	round_num:2}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:33	round_num:2}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:33	round_num:3}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:34	round_num:3}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:35	round_num:2}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:35	round_num:3}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:36	round_num:2}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:37	round_num:2}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:37	round_num:3}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:39	round_num:1}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:40	round_num:1}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:41	round_num:3}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:42	round_num:1}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:42	round_num:3}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:43	round_num:3}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:44	round_num:1}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:46	round_num:3}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:48	round_num:3}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:49	round_num:2}
1	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:50	round_num:2}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:1	round_num:1}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:11	round_num:2}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:19	round_num:3}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:20	round_num:1}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:20	round_num:2}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:21	round_num:3}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:23	round_num:3}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:26	round_num:1}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:26	round_num:2}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:27	round_num:1}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:27	round_num:2}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:28	round_num:1}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:29	round_num:2}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:31	round_num:1}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:31	round_num:3}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:32	round_num:2}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:33	round_num:2}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:34	round_num:2}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:34	round_num:3}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:35	round_num:3}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:37	round_num:2}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:38	round_num:2}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:41	round_num:1}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:42	round_num:3}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:43	round_num:1}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:43	round_num:3}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:44	round_num:3}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:45	round_num:1}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:48	round_num:3}
1	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:50	round_num:2}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:11	round_num:1}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:13	round_num:2}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:14	round_num:2}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:15	round_num:1}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:16	round_num:1}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:16	round_num:2}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:22	round_num:2}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:24	round_num:2}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:27	round_num:3}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:28	round_num:3}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:29	round_num:3}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:31	round_num:1}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:32	round_num:1}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:32	round_num:3}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:33	round_num:3}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:35	round_num:1}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:35	round_num:2}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:43	round_num:2}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:46	round_num:2}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:50	round_num:1}
1	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:50	round_num:3}
1	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:15	round_num:1}
1	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:16	round_num:2}
1	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:17	round_num:1}
1	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:18	round_num:3}
1	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:20	round_num:3}
1	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:22	round_num:2}
1	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:24	round_num:2}
1	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:27	round_num:3}
1	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:28	round_num:3}
1	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:30	round_num:3}
1	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:32	round_num:3}
1	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:33	round_num:2}
1	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:33	round_num:3}
1	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:35	round_num:2}
1	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:40	round_num:3}
1	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:10	round_num:1}
1	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:12	round_num:2}
1	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:18	round_num:1}
1	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:20	round_num:3}
1	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:26	round_num:2}
1	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:28	round_num:3}
1	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:31	round_num:3}
1	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:35	round_num:3}
1	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:36	round_num:2}
1	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:42	round_num:3}
1	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:44	round_num:3}
1	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:46	round_num:3}
1	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:47	round_num:2}
1	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:49	round_num:2}
1	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:14	round_num:2}
1	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:22	round_num:2}
1	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:24	round_num:3}
1	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:28	round_num:3}
1	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:29	round_num:2}
1	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:36	round_num:3}
1	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:37	round_num:3}
1	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:46	round_num:3}
1	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:48	round_num:3}
2	{"game_result":1	level_name:0	main_cfg:101427055	mian_level:9	round_num:1}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:22	round_num:2}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:24	round_num:1}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:24	round_num:3}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:26	round_num:2}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:29	round_num:1}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:30	round_num:2}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:30	round_num:3}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:31	round_num:1}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:32	round_num:2}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:32	round_num:3}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:33	round_num:1}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:34	round_num:2}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:36	round_num:3}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:37	round_num:1}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:38	round_num:3}
2	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:41	round_num:1}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:20	round_num:3}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:23	round_num:2}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:25	round_num:1}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:27	round_num:2}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:27	round_num:3}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:30	round_num:1}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:30	round_num:3}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:31	round_num:3}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:32	round_num:3}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:33	round_num:3}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:34	round_num:1}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:37	round_num:3}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:38	round_num:1}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:39	round_num:3}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:40	round_num:3}
2	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:42	round_num:1}
2	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:20	round_num:3}
2	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:22	round_num:1}
2	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:23	round_num:1}
2	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:26	round_num:1}
2	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:31	round_num:1}
2	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:31	round_num:3}
2	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:34	round_num:3}
2	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:35	round_num:1}
2	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:35	round_num:2}
2	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:38	round_num:3}
2	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:39	round_num:1}
2	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:41	round_num:3}
2	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:1	round_num:1}
2	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:20	round_num:1}
2	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:24	round_num:1}
2	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:29	round_num:1}
2	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:30	round_num:1}
2	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:31	round_num:3}
2	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:32	round_num:1}
2	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:32	round_num:3}
2	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:36	round_num:1}
2	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:39	round_num:3}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:21	round_num:1}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:21	round_num:2}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:25	round_num:1}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:25	round_num:3}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:29	round_num:3}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:30	round_num:1}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:30	round_num:2}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:32	round_num:3}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:33	round_num:1}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:33	round_num:3}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:36	round_num:2}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:37	round_num:1}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:38	round_num:3}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:40	round_num:3}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:41	round_num:2}
2	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:46	round_num:3}
2	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:15	round_num:2}
2	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:19	round_num:3}
2	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:29	round_num:2}
2	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:9	round_num:2}
2	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:13	round_num:2}
2	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:14	round_num:2}
2	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:19	round_num:2}
2	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:3	round_num:1}
2	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:13	round_num:2}
2	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:24	round_num:2}
2	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:15	round_num:2}
2	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:18	round_num:1}
2	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:29	round_num:3}
2	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:32	round_num:2}
2	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:47	round_num:3}
2	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:7	round_num:1}
3	{"game_result":1	level_name:0	main_cfg:101427055	mian_level:8	round_num:1}
3	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:15	round_num:3}
3	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:18	round_num:1}
3	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:21	round_num:1}
3	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:22	round_num:1}
3	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:23	round_num:1}
3	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:24	round_num:2}
3	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:26	round_num:3}
3	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:27	round_num:3}
3	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:29	round_num:3}
3	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:33	round_num:2}
3	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:33	round_num:3}
3	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:36	round_num:2}
3	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:37	round_num:2}
3	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:42	round_num:3}
3	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:19	round_num:3}
3	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:21	round_num:1}
3	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:22	round_num:1}
3	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:24	round_num:2}
3	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:24	round_num:3}
3	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:25	round_num:2}
3	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:29	round_num:2}
3	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:34	round_num:2}
3	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:34	round_num:3}
3	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:37	round_num:2}
3	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:38	round_num:2}
3	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:43	round_num:3}
3	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:18	round_num:1}
3	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:19	round_num:3}
3	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:24	round_num:3}
3	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:25	round_num:2}
3	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:25	round_num:3}
3	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:26	round_num:2}
3	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:30	round_num:2}
3	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:30	round_num:3}
3	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:35	round_num:3}
3	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:38	round_num:2}
3	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:39	round_num:2}
3	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:44	round_num:3}
3	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:21	round_num:3}
3	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:23	round_num:1}
3	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:25	round_num:3}
3	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:26	round_num:3}
3	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:28	round_num:3}
3	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:31	round_num:2}
3	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:39	round_num:2}
3	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:40	round_num:2}
3	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:45	round_num:3}
3	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:13	round_num:2}
3	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:22	round_num:3}
3	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:23	round_num:1}
3	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:24	round_num:1}
3	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:26	round_num:3}
3	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:27	round_num:3}
3	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:37	round_num:3}
3	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:40	round_num:2}
3	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:49	round_num:3}
3	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:19	round_num:2}
3	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:10	round_num:1}
3	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:19	round_num:3}
3	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:12	round_num:1}
3	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:14	round_num:1}
3	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:19	round_num:1}
3	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:19	round_num:1}
3	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:24	round_num:2}
3	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:28	round_num:2}
4	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:19	round_num:1}
4	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:19	round_num:3}
4	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:20	round_num:1}
4	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:22	round_num:3}
4	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:23	round_num:2}
4	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:23	round_num:3}
4	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:31	round_num:3}
4	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:39	round_num:3}
4	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:17	round_num:1}
4	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:20	round_num:1}
4	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:23	round_num:3}
4	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:29	round_num:3}
4	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:8	round_num:2}
4	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:21	round_num:1}
4	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:21	round_num:2}
4	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:27	round_num:3}
4	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:18	round_num:1}
4	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:22	round_num:1}
4	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:22	round_num:2}
4	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:27	round_num:2}
4	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:36	round_num:3}
4	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:16	round_num:1}
4	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:19	round_num:1}
4	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:19	round_num:2}
4	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:25	round_num:2}
4	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:28	round_num:2}
4	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:19	round_num:1}
4	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:15	round_num:1}
4	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:14	round_num:1}
4	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:19	round_num:2}
5	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:25	round_num:3}
5	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:28	round_num:3}
5	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:8	round_num:2}
5	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:1	round_num:1}
5	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:18	round_num:1}
5	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:18	round_num:2}
5	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:20	round_num:2}
5	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:26	round_num:3}
5	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:17	round_num:1}
5	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:20	round_num:2}
5	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:22	round_num:3}
5	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:21	round_num:2}
5	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:14	round_num:2}
5	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:22	round_num:2}
5	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:23	round_num:2}
5	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:24	round_num:2}
5	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:24	round_num:3}
5	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:12	round_num:2}
5	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:13	round_num:1}
5	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:19	round_num:1}
5	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:13	round_num:1}
5	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:14	round_num:1}
5	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:5	round_num:1}
5	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:14	round_num:2}
5	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:12	round_num:1}
6	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:18	round_num:3}
6	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:28	round_num:2}
6	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:16	round_num:1}
6	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:18	round_num:3}
6	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:19	round_num:2}
6	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:22	round_num:2}
6	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:15	round_num:1}
6	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:23	round_num:2}
6	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:12	round_num:2}
6	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:15	round_num:1}
6	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:17	round_num:2}
6	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:23	round_num:3}
6	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:24	round_num:2}
6	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:18	round_num:2}
6	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:14	round_num:1}
7	{"game_result":1	level_name:0	main_cfg:101427055	mian_level:7	round_num:1}
7	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:16	round_num:1}
7	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:17	round_num:2}
7	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:19	round_num:2}
7	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:21	round_num:3}
7	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:15	round_num:2}
7	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:16	round_num:2}
7	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:18	round_num:2}
7	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:18	round_num:3}
7	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:13	round_num:2}
7	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:16	round_num:2}
7	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:23	round_num:2}
7	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:17	round_num:2}
7	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:10	round_num:1}
7	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:7	round_num:1}
7	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:13	round_num:1}
7	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:5	round_num:1}
7	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:8	round_num:1}
8	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:20	round_num:3}
8	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:17	round_num:3}
8	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:12	round_num:2}
8	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:22	round_num:2}
8	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:16	round_num:1}
8	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:18	round_num:2}
8	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:12	round_num:1}
8	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:9	round_num:1}
8	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:8	round_num:1}
8	{"game_result":3	level_name:4	main_cfg:101410007	mian_level:1	round_num:3}
9	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:15	round_num:1}
9	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:17	round_num:1}
9	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:16	round_num:2}
9	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:17	round_num:2}
9	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:17	round_num:2}
9	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:15	round_num:2}
9	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:13	round_num:1}
9	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:9	round_num:1}
10	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:16	round_num:3}
10	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:17	round_num:3}
10	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:18	round_num:2}
10	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:21	round_num:2}
10	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:14	round_num:1}
10	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:14	round_num:2}
10	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:15	round_num:2}
10	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:21	round_num:2}
10	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:11	round_num:2}
10	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:14	round_num:1}
10	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:14	round_num:2}
10	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:14	round_num:1}
10	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:16	round_num:2}
10	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:17	round_num:1}
10	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:19	round_num:2}
11	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:20	round_num:2}
11	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:10	round_num:2}
11	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:10	round_num:1}
11	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:13	round_num:1}
11	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:13	round_num:1}
11	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:12	round_num:1}
11	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:19	round_num:3}
12	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:7	round_num:2}
12	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:18	round_num:1}
12	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:7	round_num:1}
12	{"game_result":2	level_name:4	main_cfg:101427056	mian_level:10	round_num:1}
13	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:15	round_num:2}
13	{"game_result":3	level_name:3	main_cfg:101410007	mian_level:1	round_num:3}
13	{"game_result":3	level_name:4	main_cfg:101410007	mian_level:1	round_num:2}
14	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:17	round_num:1}
14	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:7	round_num:1}
15	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:1	round_num:1}
15	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:11	round_num:2}
15	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:16	round_num:1}
15	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:14	round_num:2}
15	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:11	round_num:1}
15	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:15	round_num:1}
16	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:15	round_num:2}
16	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:16	round_num:2}
16	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:13	round_num:2}
16	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:15	round_num:1}
16	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:14	round_num:1}
17	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:12	round_num:1}
18	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:13	round_num:2}
18	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:9	round_num:2}
18	{"game_result":3	level_name:3	main_cfg:101410007	mian_level:1	round_num:2}
19	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:13	round_num:2}
20	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:9	round_num:1}
20	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:11	round_num:1}
20	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:12	round_num:1}
20	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:8	round_num:1}
21	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:14	round_num:2}
21	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:13	round_num:1}
21	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:12	round_num:1}
21	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:13	round_num:1}
21	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:5	round_num:1}
22	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:13	round_num:1}
23	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:10	round_num:2}
24	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:10	round_num:1}
24	{"game_result":4	level_name:0	round_num:3}
25	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:6	round_num:1}
26	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:12	round_num:2}
26	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:12	round_num:2}
27	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:14	round_num:1}
27	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:9	round_num:1}
29	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:11	round_num:1}
32	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:12	round_num:1}
35	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:9	round_num:1}
35	{"game_result":3	level_name:4	main_cfg:101410007	mian_level:1	round_num:1}
36	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:5	round_num:1}
37	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:12	round_num:1}
39	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:10	round_num:1}
39	{"game_result":3	level_name:3	main_cfg:101410007	mian_level:1	round_num:1}
45	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:11	round_num:2}
49	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:8	round_num:1}
50	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:11	round_num:1}
51	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:8	round_num:1}
53	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:8	round_num:1}
53	{"game_result":2	level_name:3	main_cfg:101427056	mian_level:9	round_num:1}
56	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:8	round_num:1}
56	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:6	round_num:1}
60	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:9	round_num:1}
63	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:11	round_num:1}
71	{"game_result":1	level_name:5	main_cfg:101427055	mian_level:10	round_num:1}
80	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:7	round_num:1}
83	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:4	round_num:1}
84	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:7	round_num:1}
94	{"game_result":1	level_name:0	main_cfg:101427055	mian_level:6	round_num:1}
107	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:10	round_num:1}
108	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:9	round_num:1}
109	{"game_result":2	level_name:2	main_cfg:101427056	mian_level:4	round_num:1}
119	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:9	round_num:1}
143	{"game_result":1	level_name:4	main_cfg:101427055	mian_level:5	round_num:1}
150	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:6	round_num:1}
170	{"game_result":4	level_name:0	round_num:2}
178	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:8	round_num:1}
203	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:8	round_num:1}
226	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:6	round_num:1}
251	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:4	round_num:1}
272	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:7	round_num:1}
278	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:7	round_num:1}
375	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:7	round_num:1}
517	{"game_result":1	level_name:3	main_cfg:101427055	mian_level:4	round_num:1}
624	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:5	round_num:1}
767	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:3	round_num:1}
882	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:5	round_num:1}
1049	{"game_result":1	level_name:2	main_cfg:101427055	mian_level:3	round_num:1}
1303	{"game_result":2	level_name:1	main_cfg:101427056	mian_level:3	round_num:1}
1341	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:6	round_num:1}
1473	{"game_result":1	level_name:0	main_cfg:101427055	mian_level:2	round_num:1}
1925	{"game_result":1	level_name:0	main_cfg:101427055	mian_level:4	round_num:1}
2081	{"game_result":1	level_name:0	main_cfg:101427055	mian_level:5	round_num:1}
2761	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:2	round_num:1}
3037	{"game_result":1	level_name:1	main_cfg:101427055	mian_level:4	round_num:1}
3188	{"game_result":1	level_name:0	main_cfg:101427055	mian_level:1	round_num:1}
4051	{"game_result":4	level_name:0	round_num:1}
5278	{"game_result":1	level_name:0	main_cfg:101427055	mian_level:3	round_num:1}
"""

def parse_data(raw):
    records = []
    for line in raw.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # 使用正则匹配: 数字 + 空白 + 数据
        match = re.match(r'^(\d+)\s+(.+)$', line)
        if not match:
            continue
        
        count = int(match.group(1))
        data_str = match.group(2)
        
        # 提取字段 - 支持多种格式
        game_result_match = re.search(r'game_result[:\"\s]*(\d+)', data_str)
        level_name_match = re.search(r'level_name[:\"\s]*(\d+)', data_str)
        mian_level_match = re.search(r'mian_level[:\"\s]*(\d+)', data_str)
        round_num_match = re.search(r'round_num[:\"\s]*(\d+)', data_str)
        
        if game_result_match:
            record = {
                'count': count,
                'game_result': int(game_result_match.group(1)),
                'level_name': int(level_name_match.group(1)) if level_name_match else None,
                'mian_level': int(mian_level_match.group(1)) if mian_level_match else None,
                'round_num': int(round_num_match.group(1)) if round_num_match else None
            }
            records.append(record)
    
    return records

def analyze_data(records):
    success_records = [r for r in records if r['game_result'] == 1]
    fail_records = [r for r in records if r['game_result'] == 2]
    resurrection_records = [r for r in records if r['game_result'] == 3]
    restart_records = [r for r in records if r['game_result'] == 4]
    
    total_success_count = sum(r['count'] for r in success_records)
    total_fail_count = sum(r['count'] for r in fail_records)
    total_resurrection_count = sum(r['count'] for r in resurrection_records)
    total_restart_count = sum(r['count'] for r in restart_records)
    
    print("=" * 60)
    print("游戏数据分析报告")
    print("=" * 60)
    
    print("\n【一、整体概览】")
    print(f"  通关(Success)总人次: {total_success_count:,}")
    print(f"  失败(Fail)总人次: {total_fail_count:,}")
    print(f"  复活(Resurrection)总人次: {total_resurrection_count:,}")
    print(f"  重开(Restart)总人次: {total_restart_count:,}")
    
    total_play = total_success_count + total_fail_count
    if total_play > 0:
        success_rate = total_success_count / total_play * 100
        fail_rate = total_fail_count / total_play * 100
        print(f"\n  通关率(不含复活/重开): {success_rate:.2f}%")
        print(f"  失败率(不含复活/重开): {fail_rate:.2f}%")
    
    print("\n" + "=" * 60)
    print("【二、通关数据分析 (game_result=1)】")
    print("=" * 60)
    
    success_by_level = defaultdict(int)
    for r in success_records:
        if r['level_name'] is not None:
            success_by_level[r['level_name']] += r['count']
    
    print("\n  按大关卡(level_name)分布:")
    for level in sorted(success_by_level.keys()):
        print(f"    level_name={level}: {success_by_level[level]:,} 人次")
    
    success_by_mian = defaultdict(int)
    for r in success_records:
        if r['mian_level'] is not None:
            success_by_mian[r['mian_level']] += r['count']
    
    print("\n  按子关卡(mian_level)分布 (Top 15 热门通关关卡):")
    sorted_mian = sorted(success_by_mian.items(), key=lambda x: x[1], reverse=True)[:15]
    for mian, cnt in sorted_mian:
        print(f"    第{mian}关: {cnt:,} 人次通关")
    
    success_by_round = defaultdict(int)
    for r in success_records:
        if r['round_num'] is not None:
            success_by_round[r['round_num']] += r['count']
    
    print("\n  按轮次(round_num)分布:")
    for rnd in sorted(success_by_round.keys()):
        print(f"    第{rnd}轮: {success_by_round[rnd]:,} 人次")
    
    print("\n" + "=" * 60)
    print("【三、失败数据分析 (game_result=2)】")
    print("=" * 60)
    
    fail_by_level = defaultdict(int)
    for r in fail_records:
        if r['level_name'] is not None:
            fail_by_level[r['level_name']] += r['count']
    
    print("\n  按大关卡(level_name)分布:")
    for level in sorted(fail_by_level.keys()):
        print(f"    level_name={level}: {fail_by_level[level]:,} 人次")
    
    fail_by_mian = defaultdict(int)
    for r in fail_records:
        if r['mian_level'] is not None:
            fail_by_mian[r['mian_level']] += r['count']
    
    print("\n  按子关卡(mian_level)分布 (Top 15 高失败关卡):")
    sorted_fail_mian = sorted(fail_by_mian.items(), key=lambda x: x[1], reverse=True)[:15]
    for mian, cnt in sorted_fail_mian:
        print(f"    第{mian}关: {cnt:,} 人次失败")
    
    fail_by_round = defaultdict(int)
    for r in fail_records:
        if r['round_num'] is not None:
            fail_by_round[r['round_num']] += r['count']
    
    print("\n  按轮次(round_num)分布:")
    for rnd in sorted(fail_by_round.keys()):
        print(f"    第{rnd}轮: {fail_by_round[rnd]:,} 人次")
    
    print("\n" + "=" * 60)
    print("【四、各大关卡通关率对比】")
    print("=" * 60)
    
    all_levels = set(success_by_level.keys()) | set(fail_by_level.keys())
    print("\n  level_name | 通关人次 | 失败人次 | 通关率")
    print("  " + "-" * 50)
    for level in sorted(all_levels):
        s = success_by_level.get(level, 0)
        f = fail_by_level.get(level, 0)
        total = s + f
        rate = s / total * 100 if total > 0 else 0
        print(f"  {level:^10} | {s:>8,} | {f:>8,} | {rate:>6.2f}%")
    
    print("\n" + "=" * 60)
    print("【五、关卡流失分析 (失败集中区域)】")
    print("=" * 60)
    
    print("\n  早期关卡(1-10关)失败人次:")
    early_fail = sum(cnt for mian, cnt in fail_by_mian.items() if 1 <= mian <= 10)
    print(f"    {early_fail:,} 人次")
    
    print("\n  中期关卡(11-20关)失败人次:")
    mid_fail = sum(cnt for mian, cnt in fail_by_mian.items() if 11 <= mian <= 20)
    print(f"    {mid_fail:,} 人次")
    
    print("\n  后期关卡(21-50关)失败人次:")
    late_fail = sum(cnt for mian, cnt in fail_by_mian.items() if 21 <= mian <= 50)
    print(f"    {late_fail:,} 人次")

if __name__ == "__main__":
    records = parse_data(raw_data)
    print(f"共解析 {len(records)} 条记录\n")
    analyze_data(records)
