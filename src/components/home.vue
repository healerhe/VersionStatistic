<template>
  <div class="home">
    <div class="header">
      <div class="container">
        <span class="title">iSPECO产品中集成的3rd软件list</span>
      </div>
    </div>
    <div class="main">
      <a-back-top />
      <div class="search">
        <a-input-search placeholder="输入user/repo or type or product"
                        v-model="search_text"
                        @search="onSearch"
                        enterButton="搜索..." />
        <div class="tips">
          <strong :style="{ marginRight: 8 }">常用类别:</strong>
          <a-radio-group default-value="" button-style="solid">
            <a-radio-button value="" class="tips-tag tag-all" @click="tagChange()" >
              All
            </a-radio-button>
            <template v-for=" tag in tags">
              <a-radio-button :value="tag" :key="tag"
                  class="tips-tag"
                  @click="tagChange(tag)">
                {{tag}}
              </a-radio-button>
            </template>
          </a-radio-group>
        </div>

      </div>
      <div class="content">
        <!-- <a-divider orientation="left">项目列表</a-divider> -->
        <a-spin :spinning="spinning">
          <a-list itemLayout="horizontal"
                  :pagination="pagination"
                  :dataSource="listData"
                  v-if="listData.length !== 0">
            <div slot="header"
                 class="list-header"><b>更新时间: </b>{{ updated_at.toLocaleString() }} <b> 统计数目: </b>{{ total }}
            </div>
            <a-list-item slot="renderItem"
                         slot-scope="item"
                         key="item.title">
              <a-list-item-meta>
                <div slot="description">
                  <span class="tag-title">类别: </span>
                  <a-tag color="#2db7f5"
                         @click="tagChange(item.type)">{{ item.type }}</a-tag>

                  <div style="display: inline-block;">
                    <span class="tag-title">产品-集成方式-(使用版本): </span>
                    <template v-if="item.current_version">
                      <a-list itemLayout="horizontal" style="display: inline-block; vertical-align: top;"
                        :dataSource="item.current_version">
                        <a-list-item slot="renderItem"
                          style="padding-top: 0;border-bottom:0px"
                          slot-scope="version, index"
                          key="version">
                          <a-tag color="#2db7f5">{{ item.integration_method[index] +"-("+ version+")" || "unknown" }}</a-tag>
                        </a-list-item>
                      </a-list>
                    </template>
                    <template v-else>
                      <a-tag color="#2db7f5">{{ item.currentVersion||"none" }}</a-tag>
                    </template>
                   
                  </div>
                  <!-- <span class="tag-title">产品/集成方式: </span>
                  <a-tag color="#2db7f5">{{ item.integration_method || "unknown" }}</a-tag>
                  <span class="tag-title">当前集成版本: </span>
                  <a-tag color="#2db7f5">{{ item.currentVersion||"none" }}</a-tag> -->
                  <span class="tag-title">最新{{ item.html_url.indexOf('release') !== -1 ? '版本' : 'Tag' }}: </span>
                  <a-tag color="#108ee9"
                           @click="tagClick(item.project, item.body)" >{{ item.tag_name || item.name }}</a-tag>
                  <a-tooltip placement="top"
                             title="点击查看最近版本">
                    <a-tag color="#5bd1d7"
                           @click="lastClick(item.project, item.html_url, item.repo, item.hosting)">Releases {{ item.html_url.indexOf('release') !== -1 ? '版本' : 'Tag' }}</a-tag>
                  </a-tooltip>
                  <span class="tag-title">Release date: </span>
                  <a-tag color="#F17F42">{{ item.created_at || "None"  }}</a-tag>

                  <span class="tag-title">访问地址: </span>
                  <a-tag color="#F17F42">
                    <a target="_blank" :href="item.repo_url" >{{ item.repo_url || "None"  }}</a>
                  </a-tag>

                  <div class="version-info"
                       v-if="item.project === project">
                    <a-spin :spinning="versionSpinning">
                      <div v-if="showLast">
                        <a-divider orientation="left">
                          <span style="font-size: 16px;">最近{{ item.html_url.indexOf('release') !== -1 ? '版本' : 'Tag' }}</span>
                        </a-divider>
                        <a-timeline>
                          <template v-for="(last, index) in filterLastData()">
                            <a-timeline-item :key="index">
                              <a target="_blank"
                                 :href="last.html_url" >{{ last.tag_name || last.name }}</a> [{{last.created_at}}]
                            </a-timeline-item>
                          </template>
                        </a-timeline>
                      </div>
                      <div v-if="showInfo">
                        <a-divider orientation="left">
                          <a target="_blank"
                             class="info-title"
                             :href="item.html_url">{{ item.tag_name || item.name }} [{{item.created_at}}]</a></a-divider>
                        <div class="repo-desc"
                             v-html="readmeContent">
                        </div>
                      </div>
                    </a-spin>
                  </div>
                </div>
                <a slot="title"
                   class="list-title"
                   target="_blank"
                   :id="item.project"
                   :href="item.repo_url">{{ item.project[0].toUpperCase() + item.project.slice(1) }}</a>
              </a-list-item-meta>
            </a-list-item>
          </a-list>
        </a-spin>
      </div>
    </div>

  </div>
</template>

<script>
import marked from 'marked'
import { Button, Icon, List, BackTop, Tooltip, Tag, Input, Spin, Switch, Divider, Timeline, Popover, Radio } from 'ant-design-vue'
import { formatTime } from '@/utils/util'
import { DOCKERHUB, GITHUB, RC, ALPHA, BETA } from '@/assets/constant'
// import $ from 'jquery'

export default {
  name: 'home',
  data () {
    return {
      // 'unknown'
      tags: [],
      listData: [],
      updated_at: '',
      total: '',
      search_text: '',
      pagination: {
        pageSize: 10,
        size: 'small',
        onChange: (page) => {
          document.querySelector('#app').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          })
        }
      },
      readmeContent: '',
      project: '',
      spinning: true,
      shieldsShow: false,
      timer: '',
      showInfo: false,
      showLast: false,
      versionSpinning: true,
      lastData: [],
      lastProject: '',
      searchData: [],
      searchCount: 0,
      trending: false,
      trendData: [],
      runDay: parseInt((new Date().getTime() - new Date(Date.parse('2019-09-18'.replace(/-/g, '/'))).getTime()) / 1000 / 3600 / 24)
    }
  },
  components: {
    AButton: Button,
    AIcon: Icon,
    AList: List,
    AListItem: List.Item,
    AListItemMeta: List.Item.Meta,
    ABackTop: BackTop,
    ATooltip: Tooltip,
    ATag: Tag,
    AInputSearch: Input.Search,
    ASpin: Spin,
    ASwitch: Switch,
    ADivider: Divider,
    ATimeline: Timeline,
    ATimelineItem: Timeline.Item,
    APopover: Popover,
    ARadioGroup: Radio.Group,
    ARadio: Radio,
    ARadioButton: Radio.Button
  },
  computed: {
  },
  watch: {
  },
  methods: {
    filterLastData () {
      let _this = this;
      return this.lastData.filter(function (item) {
        // let name = item.name.toLowerCase();
        let tag_name = item.tag_name.toLowerCase();
        // let nameFlag = name && (name.indexOf('rc') !== -1 || name.indexOf('alpha') !== -1 || name.indexOf('beta') !== -1)
        let tagNameFlag = tag_name && !_this._isRelease(tag_name)
        // console.log("name:"+name, nameFlag ,  tagNameFlag);
        return !tagNameFlag
      })
    },
    _isRelease(tag) {
      if (tag.indexOf(RC) !== -1 || tag.indexOf(ALPHA) !== -1 || tag.indexOf(BETA) !== -1) {
        return false
      }
      return true
    },
    trendClick () {
      this.spinning = true
      this.listData = []
      if (this.trending) {
        this.searchData = this.trendData
        this.spinning = false
        return
      }
      this._getGithubTrending()
    },
    lastClick (project, url, repo, hosting) {
      let _this = this;
      this.versionSpinning = true
      this.lastData = []
      if (this.project === project && this.showLast) {
        this.showLast = false
        this.project = ''
        return
      }
      
      this.$axios.get('static/data/tags.json').then((res) => {
        let result = res.data[repo]
        if (result && result.length > 0) {
          _this.lastData = result;
          _this.versionSpinning = false
        } else {
          _this._getTagsByOnline(project, url, repo, hosting)
        }
        this.project = project
        this.lastProject = project
        this.showLast = true
        this.showInfo = false
      }).catch((e) => {
        console.log(e)
      })
    },
    tagClick (project, data) {
      this.versionSpinning = true
      if (this.project === project && this.showInfo) {
        this.readmeContent = ''
        this.project = ''
        this.showInfo = false
        return
      }
      this.readmeContent = marked(data || 'None', { breaks: true })
      this.project = project
      this.showInfo = true
      this.showLast = false
      this.versionSpinning = false
    },
    tagChange (value) {
      this.search_text = value
      this._getData(value)
    },
    onSearch (value) {
      if (typeof value === 'undefined' || value === null || value === '') {
        this._getData()
      } else {
        this._getData(value)
      }
    },
    _getData (search = '') {
      this.spinning = true
      this.$axios.get('static/data/data.json').then((rep) => {
        this.listData = rep.data['data']
        this.listData.forEach((e) => {
          e['created_at'] = formatTime(new Date(e['created_at']))
          let type = e['type']
          if (this.tags.indexOf(type) === -1) {
            this.tags.push(type)
          }
        })
        this.total = rep.data['total']
        this.updated_at = formatTime(new Date(rep.data['updated_at']))
        if (search !== '') {
          let lowerCaseSearch = search.toLowerCase()
          for (let i = 0; i < this.listData.length; i++) {
            let productUse = this.listData[i]['integration_method'].join(',').toLowerCase()
            if (this.listData[i]['type'].toLowerCase().indexOf(lowerCaseSearch) === -1 && this.listData[i]['project'].toLowerCase().indexOf(lowerCaseSearch) === -1 && productUse.indexOf(lowerCaseSearch) === -1) {
              this.listData.splice(i--, 1)
            }
          }
          if (this.listData.length === 0) {
            this._getGithubLatest(search)
            if (this.listData.length === 0) {
              this._getGithubTags(search, 'listData')
            }
            if (this.listData.length === 0) {
              this._getSearchGithub(search)
            }
          }
        }
        this.spinning = false
      }).catch((e) => {
        this.$message.error('获取数据失败!')
        console.log(e)
        this.spinning = false
      })
    },
    _getGithubTags (repo, target) {
      let graphqlUrl = 'https://api.github.com/graphql'
      let postData = {
        'query': '{repository(owner: "' + repo.split('/')[0] + '", name: "' + repo.split('/')[1] + '") {refs(refPrefix: "refs/tags/", first: 10, orderBy: {field: TAG_COMMIT_DATE, direction: DESC}) {edges {node {name target {commitUrl ... on Tag {message tagger {date}} ... on Commit {committedDate}}}}}}}'
      }
      let token = '99510f2ccf40e496d1e97dbec9f31cb16770b884'
      let headers = { 'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'token ' + token }
      this.$axios.post(graphqlUrl, postData, { headers }).then((res) => {
        if (res.data['data']['repository'] !== null && res.data['data']['repository'].hasOwnProperty('refs')) {
          let lastTags = res.data['data']['repository']['refs']['edges']
          this[target] = []
          for (let item in lastTags) {
            this[target].push({
              'tag_name': lastTags[item]['node']['name'],
              'repo_url': 'https://github.com/' + repo,
              'html_url': lastTags[item]['node']['target']['commitUrl'] || '',
              'created_at': lastTags[item]['node']['target'].hasOwnProperty('tagger') ? formatTime(new Date(lastTags[item]['node']['target']['tagger']['date'])) : formatTime(new Date(lastTags[item]['node']['target']['committedDate'])),
              'project': repo,
              'repo': repo,
              'body': lastTags[item]['node']['target']['message'],
              'hosting': 'github',
              'type': 'None'
            })
            if (target === 'listData') {
              this.total = this.listData.length
              this.updated_at = new Date()
              break
            }
          }
        }
        if (this[target].length === 0) {
          this.$message.error('未找到项目的tags!')
        }
        this.versionSpinning = false
        this.spinning = false
      }).catch((e) => {
        this.$message.error('获取项目的tags失败!')
        console.log(e)
        this.spinning = false
      })
    },
    _getGithubRelases (repo) {
      let repoUrl = 'https://api.github.com/repos/' + repo + '/releases?per_page=10'
      this.$axios.get(repoUrl).then((res) => {
        this.lastData = res.data
        this.versionSpinning = false
      }).catch((e) => {
        this.$message.error('获取项目的releases失败!')
        console.log(e)
        this.spinning = false
      })
    },
    _getGithubLatest (repo) {
      let repoUrl = 'https://api.github.com/repos/' + repo + '/releases/latest'
      this.$axios.get(repoUrl).then((res) => {
        let data = {
          'name': res.data['name'],
          'tag_name': res.data['tag_name'],
          'html_url': res.data['html_url'],
          'repo_url': 'https://github.com/' + repo,
          'body': res.data['body'],
          'created_at': formatTime(new Date(res.data['created_at'])),
          'project': repo,
          'repo': repo,
          'hosting': 'github',
          'type': 'None'
        }
        this.listData = [data]
        this.total = this.listData.length
        this.updated_at = new Date()
        this.spinning = false
      }).catch((e) => {
        this.$message.error('没有找到项目的latest release版本!')
        console.log(e)
      })
    },
    _getSearchGithub (repo) {
      let searchUrl = 'https://api.github.com/search/repositories?q=' + repo + '+in:name&sort=stars&order=desc&per_page=10'
      this.$axios.get(searchUrl).then((res) => {
        this.searchData = []
        this.searchCount = res.data['total_count']
        for (let item in res.data['items']) {
          let data = {
            'full_name': res.data['items'][item]['full_name'],
            'html_url': res.data['items'][item]['html_url'],
            'description': res.data['items'][item]['description'],
            'forks_count': res.data['items'][item]['forks_count'],
            'stargazers_count': res.data['items'][item]['stargazers_count'],
            'language': res.data['items'][item]['language'],
            'updated_at': formatTime(new Date(res.data['items'][item]['updated_at']))
          }
          this.searchData.push(data)
        }
        this.spinning = false
      }).catch((e) => {
        this.$message.error('没有搜索到项目!')
        console.log(e)
      })
    },
    _getGithubTrending () {
      let url = 'https://github-trending-api.now.sh/repositories'
      this.$axios.get(url).then((res) => {
        this.trendData = []
        for (let item in res.data) {
          let data = {
            'full_name': res.data[item]['author'] + '/' + res.data[item]['name'],
            'html_url': res.data[item]['url'],
            'description': res.data[item]['description'],
            'forks_count': res.data[item]['forks'],
            'stargazers_count': res.data[item]['stars'],
            'language': res.data[item]['language'],
            'currentPeriodStars': res.data[item]['currentPeriodStars']
          }
          this.trendData.push(data)
        }
        this.searchData = this.trendData
        this.spinning = false
        this.trending = true
      }).catch((e) => {
        this.$message.error('获取失败!')
        console.log(e)
      })
    },
    _getDockerHubTags (repo) {
      let repoUrl = 'http://hub.docker.com/v2/repositories/'+repo+'/tags/?page_size=10&page=1';
      let results = []
      this.$axios.get(repoUrl).then((res) => {
        console.log(res)
        res.data.forEach ((result_item, index) => {
          let nameTmp = result_item['name'].toLowerCase()
          let data = {
            'tag_name': result_item['name'],
            'name': result_item['name'],
            'html_url': latest_url,
            'repo_url': 'https://hub.docker.com/r/' + repo,
            'created_at': result_item['last_updated'],
            'body': result_item['last_updated'] + ' test'
          }
          result.push(data)
        })
        this.lastData = result
        this.versionSpinning = false
      }).catch((e) => {
        this.$message.error('获取项目的releases失败!')
        console.log(e)
        this.spinning = false
      })
    },
    _getTagsByFile (repo) {
      this.$axios.get('static/data/tags.json').then((res) => {
        console.log(repo, res.data[repo])
        return res.data[repo]
      }).catch((e) => {
        return []
      })
    },
    _getTagsByOnline (project, url, repo, hosting) {
      if (hosting.toLowerCase().indexOf(DOCKERHUB) !== -1) {
          this._getDockerHubTags(repo)
        } else {
          if (this.lastProject !== project && url.indexOf('release') !== -1) {
            this._getGithubRelases(repo)
          } else if (this.lastProject !== project && url.indexOf('commit') !== -1) {
            this._getGithubTags(repo, 'lastData')
          } else {
            this.versionSpinning = false
          }
        }
    }
  },
  mounted () {
    this._getData()
  },
  beforeDestroy () {
    this.timer && clearTimeout(this.timer)
  }
}
</script>

<style lang=less scoped>
@min-width: 1000px;

.home {
  width: 100%;
  height: 100%;
}
.header {
  z-index: 100;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 80px;
  line-height: 80px;
  background: #fff;
}
.container {
  height: 100%;
  @media screen {
    @media (min-width: @min-width) {
      width: 80%;
    }
  }
  margin: 0 auto;
  padding: 0 10px;
  border-bottom: 1px solid #dcdfe6;
}
.title {
  color: #409eff;
  font-size: 26px;
  font-weight: 500;
  font-family: "微软雅黑";
  @media screen {
    @media (max-width: @min-width) {
      padding-left: 5px;
    }
  }
}
.title-desc {
  color: rgba(0, 0, 0, 0.45);
  margin-left: 10px;
  @media screen {
    @media (max-width: @min-width) {
      font-size: 12px;
    }
  }
}
.list-title {
  font-size: 16px;
  font-weight: bolder;
  font-family: "微软雅黑";
}
.main {
  position: relative;
  @media screen {
    @media (min-width: @min-width) {
      width: 80%;
    }
  }
  height: -webkit-calc(100% - 80px);
  height: -moz-calc(100% - 80px);
  height: calc(100% - 80px);
  margin: 0 auto;
  padding: 10px 0;
  top: 80px;
}
.search {
  @media screen {
    @media (min-width: @min-width) {
      width: 50%;
    }
    @media (max-width: @min-width) {
      font-size: 12px;
      padding: 20px 10px 20px;
    }
  }
  margin: 0 auto;
  text-align: center;
  padding: 20px 10px 10px;
}
.content {
  width: 100%;
  padding: 0px 80px 20px 80px;
  @media screen {
    @media (max-width: @min-width) {
      padding: 0 20px 20px 20px;
    }
  }
}
.ant-list-item-meta-description {
  @media screen {
    @media (max-width: @min-width) {
      font-size: 12px;
    }
  }
  .tag-title {
    @media screen {
      @media (max-width: @min-width) {
        display: none;
      }
    }
    display: inline-block;
    margin-bottom: 10px;
  }
  .ant-tag {
    @media screen {
      @media (max-width: @min-width) {
        margin: 0;
      }
    }
  }
}
.tips {
  margin-top: 10px;
  font-size: 14px;
  text-align: left;
}
.tips-tag {
  @media screen {
    @media (max-width: @min-width) {
      font-size: 12px;
    }
  }
  margin-right: 5px;
  margin-bottom: 5px;
  border-radius: 4px;
}
.tag-all {
   background: #df405a;
   color: #ffffff;
}
.version-info {
  margin: 20px;
  color: black;
}
.header-switch {
  float: right;
}
.footer {
  text-align: center;
  line-height: 32px;
  padding: 20px 0;
  color: rgba(0, 0, 0, 0.45);
  @media screen {
    @media (max-width: @min-width) {
      font-size: 12px;
    }
  }
}
.list-header {
  @media screen {
    @media (max-width: @min-width) {
      font-size: 12px;
    }
  }
}
.info-title {
  font-size: 20px;
  @media screen {
    @media (max-width: @min-width) {
      font-size: 14px;
    }
  }
}
.repo-desc {
  width: 100%;
  word-break: break-word;
  @media screen {
    @media (max-width: @min-width) {
      font-size: 12px;
    }
  }

  /deep/ img {
    width: 100%;
  }
  /deep/ pre code {
    display: block;
    overflow: auto;
    background: #f4f4f4;
    padding: 5px 10px;
    border: 1px solid #eee;
    word-wrap: break-word;
    white-space: pre-wrap;
  }
  /deep/ code {
    overflow: auto;
    padding: 1px;
    background: #f4f4f4;
    border: 1px solid #eee;
    word-wrap: break-word;
    white-space: pre-wrap;
  }
}
</style>
